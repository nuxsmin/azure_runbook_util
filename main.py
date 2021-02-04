#!/usr/bin/env python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("action",
                    choices=["vm.power.schedule"],
                    help="Action to be performed")

parser.add_argument("--dry_run",
                    action="store_true",
                    help="Perform a trial run with no changes made")

parser.add_argument("--debug",
                    action="store_true",
                    help="Set logging level to DEBUG")

args = parser.parse_args()

if args.action == "vm.power.schedule":
    from azure_runbook_util import vm_ops

    vm_power_schedule = vm_ops.VmPowerSchedule(dry_run=args.dry_run, debug=args.debug)
    vm_power_schedule.run()
