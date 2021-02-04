import logging
import os
import re

import azure.mgmt.compute
import azure.mgmt.resource

from azure_runbook_util import util
from azure_runbook_util.ops_base import OpsBase

if not os.getenv("CI_RUN_ID"):
    from azure_runbook_util.azure_credentials import azure_credential, runas_connection

_VM_STATUS_RUNNING = "VM running"
_VM_STATUS_DEALLOCATED = "VM deallocated"
_VM_STATUS_STOPPED = "VM stopped"
_TAG_POWER_OFF = "VMPowerOff"
_TAG_POWER_ON = "VMPowerOn"
_TAG_POWER_SKIP = "VMPowerSkip"
_TAG_POWER_DAYS = "VMPowerDays"
_DEFAULT_DAYS = list(range(0, 5))
_DAYS_REGEX = re.compile("[1-7]{1,7}(?=[|,\\s\\-]|$)")

logger = logging.getLogger(__name__)


class VmPowerProcess:
    _skipped = {
        "power_tag": [],
        "range": [],
        "day": [],
        "tag": []
    }
    _done = {
        "power_on": [],
        "power_off": []
    }

    @classmethod
    def skip_by_tag(cls, vm_id: str):
        cls._skipped["tag"].append(vm_id)

    @classmethod
    def skip_by_power_tag(cls, vm_id: str):
        cls._skipped["power_tag"].append(vm_id)

    @classmethod
    def skip_by_range(cls, vm_id: str):
        cls._skipped["range"].append(vm_id)

    @classmethod
    def skip_by_day(cls, vm_id: str):
        cls._skipped["day"].append(vm_id)

    @classmethod
    def done_power_on(cls, vm_id: str):
        cls._done["power_on"].append(vm_id)

    @classmethod
    def done_power_off(cls, vm_id: str):
        cls._done["power_off"].append(vm_id)

    @classmethod
    def get_by_tag(cls):
        return list(cls._skipped["tag"])

    @classmethod
    def get_by_power_tag(cls):
        return list(cls._skipped["power_tag"])

    @classmethod
    def get_by_range(cls):
        return list(cls._skipped["range"])

    @classmethod
    def get_by_day(cls):
        return list(cls._skipped["day"])

    @classmethod
    def get_by_power_on(cls):
        return list(cls._done["power_on"])

    @classmethod
    def get_by_power_off(cls):
        return list(cls._done["power_off"])


class VmPowerTags:
    def __init__(self,
                 on: str = _TAG_POWER_ON,
                 off: str = _TAG_POWER_OFF,
                 skip: str = _TAG_POWER_SKIP,
                 days: str = _TAG_POWER_DAYS) -> None:
        self.days = days
        self.skip = skip
        self.off = off
        self.on = on


class VmPowerSchedule(OpsBase):
    def __init__(self,
                 dry_run: bool = False,
                 debug: bool = False,
                 wait_for_action: bool = False,
                 power_tags: VmPowerTags = VmPowerTags()) -> None:
        """
        :param dry_run: Perform a trial run with no changes made
        :param debug: Set logging level to DEBUG
        :param wait_for_action: Set to True to perform synchronous power cycle actions
        :param power_tags: An instance of VmPowerTags that holds the name of the tags to lookup
        """
        super().__init__(dry_run, debug, wait_for_action)

        self.vms_process = VmPowerProcess()
        self.compute_client = None
        self.power_tags = power_tags

        if debug:
            logger.setLevel(logging.DEBUG)

    def run(self) -> None:
        """
        Process all the VMs in the subscription and run the appropriate action for the tags and status
        :return:
        """
        # Shows on the screen the current time
        logger.info("Current time: %s", self.now.time())

        self.compute_client = azure.mgmt.compute.ComputeManagementClient(
            azure_credential(),
            str(runas_connection()["SubscriptionId"]))

        vms_list = self.compute_client.virtual_machines.list_all()

        logger.debug("Listing VMs")

        for vm in vms_list:
            logger.debug("Checking VM (%s) (%s)", vm.name, vm.id)

            if vm.tags:
                logger.debug("Getting tags from VM (%s)", vm.name)
                logger.debug("Lookup tags: %s", self.power_tags.__dict__)

                tag_off = vm.tags.get(self.power_tags.off)
                tag_on = vm.tags.get(self.power_tags.on)
                tag_days = vm.tags.get(self.power_tags.days)
                tag_skip = vm.tags.get(self.power_tags.skip)

                if tag_skip:
                    self.vms_process.skip_by_tag(vm.id)

                    logger.info("VM skipped by tag (%s)", vm.name)
                    continue

                if not tag_on or not tag_off:
                    self.vms_process.skip_by_power_tag(vm.id)

                    logger.info("VM doesn't contains any power tags (%s)", vm.name)
                    continue

                if self.is_scheduled(tag_days):
                    resource_group = vm.id.split("/")[4]

                    action = self.process_vm(resource_group, vm, int(tag_on), int(tag_off))

                    if not action:
                        self.vms_process.skip_by_range(vm.id)

                        logger.info("No action (hour/status)")
                else:
                    self.vms_process.skip_by_day(vm.id)

                    logger.info("No action (day)")

                message = dict(
                    vm_name=vm.name,
                    vm_id=vm.id,
                    skip=tag_skip,
                    days=tag_days,
                    power_on=tag_on,
                    power_off=tag_off
                )

                logger.info("power.vm_data %s", util.get_json(message))
            else:
                self.vms_process.skip_by_tag(vm.id)

        logger.info("power.stats %s", util.get_json(self.get_stats()))

    def get_statuses(self, resource_group: str, vm) -> tuple:
        """
        Get the statuses from the VM instance view
        :param resource_group: The VM resource group
        :param vm: The VM instance
        :return: A tuple of statuses
        """
        logger.debug("Get VM statuses")

        current_vm = self.compute_client.virtual_machines.get(
            resource_group_name=resource_group,
            vm_name=vm.name,
            expand="InstanceView")

        statuses = tuple([status.display_status for status in current_vm.instance_view.statuses])

        logger.debug("Statuses: %s", statuses)

        return statuses

    def process_vm(self, resource_group: str, vm, start: int, end: int) -> bool:
        """
        Process a VM and power on/off upon the time range and VM status
        :param resource_group: The VM resource group
        :param vm: The VM instance
        :param start: The time to start the VM
        :param end: The time to stop the VM
        :return: Whether an action has been taken
        """
        logger.debug("Process VM")

        statuses = self.get_statuses(resource_group, vm)

        is_running = _VM_STATUS_RUNNING in statuses
        is_deallocated = _VM_STATUS_DEALLOCATED in statuses
        is_stopped = _VM_STATUS_STOPPED in statuses
        tag_in_range = util.time_in_range(start, end, self.now.hour)

        if not tag_in_range and is_running:
            logger.info("Action: Power OFF")

            self.vms_process.done_power_off(vm.id)

            if self.dry_run:
                logger.info("Dry run. Work ends here.")
                return True

            async_action = self.compute_client.virtual_machines.deallocate(resource_group, vm.name)

            if self.wait_for_action:
                async_action.wait()

            return True

        if tag_in_range and (is_deallocated or is_stopped):
            logger.info("Action: Power ON")

            self.vms_process.done_power_on(vm.id)

            if self.dry_run:
                logger.info("Dry run. Work ends here.")
                return True

            async_action = self.compute_client.virtual_machines.start(resource_group, vm.name)

            if self.wait_for_action:
                async_action.wait()

            return True

        return False

    def is_scheduled(self, days: str) -> bool:
        """
        Check whether the VM has been scheduled for the given days
        :param days: A string with the days separated by commas
        :return: Whether is scheduled
        """
        logger.debug("Check scheduled")

        weekday = self.now.today().weekday() + 1

        if days and _DAYS_REGEX.match(days):
            scheduled_days = tuple(map(lambda o: int(o), _DAYS_REGEX.findall(days)))

            return weekday in scheduled_days

        default_days = tuple(map(lambda o: int(o) + 1, _DEFAULT_DAYS))

        logger.debug("Defaulting scheduled days to: %s", default_days)

        return weekday in default_days

    def get_stats(self):
        """
        Return the VMs processed stats
        :return:
        """
        return dict(
            skipped_by_tag=self.vms_process.get_by_tag(),
            skipped_by_power_tag=self.vms_process.get_by_power_tag(),
            skipped_by_day=self.vms_process.get_by_day(),
            skipped_by_range=self.vms_process.get_by_range(),
            done_power_on=self.vms_process.get_by_power_on(),
            done_power_off=self.vms_process.get_by_power_off()
        )
