#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("action",
                    choices=["vm.power.schedule"],
                    help="Action to be performed")

args = parser.parse_args()

if args.action == "vm.power.schedule":
    from azure_runbook_util import vm_ops

    vm_power_schedule = vm_ops.VmPowerSchedule()
    vm_power_schedule.run()
