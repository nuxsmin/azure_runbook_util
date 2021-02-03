# Azure Runbook utilities

This library is intended to be run into an Azure Runbook using **Python 3**.

# Utilities

## VM Power Schedule

This utility allows to schedule a power on/off cycle by setting tags on VM instance type resources.

The power cycle will be run if the VM instance is in the correct state, that is if it needs to be powered on, it will
run if the instance is in `VM deallocated` or `VM stopped` statuses and if it needs to be powered off, it will run if
the instance is in `VM running` status.

If the VM instance is outside the time range and its status is `VM running` it will be powered off.

You can setup an hourly schedule basis, so it will check every hour for the correct power status of all VMs in the
subscription.

### Tags implemented

|Tag name|Value|Default|Example|Description|
|--------|-----|-------|-------|-----------|
|VMPowerOn|number|-|23|Set the hour in which the VM should be powered ON|
|VMPowerOff|number|-|4|Set the hour in which the VM should be powered OFF|
|VMPowerDays|string|1,2,3,4|1,3,5,7|Set the days (separated by any character) in which the action should be performed|
|VMPowerSkip|any|1|-|Skip the VM while this tag is set|

### Power transitions implemented:

|Between time range|Initial Status|Final status|Description|
|:------------------:|--------------|------------|-----------|
|Yes|VM deallocated|VM running|You'd be billed for the instance|
|Yes|VM stopped|VM running|You'd be billed for the instance|
|No|VM running|VM deallocated|You wouldn't be billed for the instance|

**Note: please be aware that a time range between two days won't trigger any action if the scheduled days don't match.**

### Usage

The first step is to upload the utilities package and dependencies to Python packages (under Shared Resources) in the
Azure Automation Account.

The next step is to create a **Python 3** Runbook with the following code:

```python
from azure_runbook_util import vm_ops

vm_power_schedule = vm_ops.VmPowerSchedule(False)  # Set to True if you need to perform synchronous power cycle actions 
vm_power_schedule.run()
```

# Development

In order to develop your own implementation, you need to install and configure the Azure Automation python emulated
assets from https://github.com/azureautomation/python_emulated_assets.