# Azure Runbook utilities

This library is intended to be run within an Azure Runbook using **Python 3**.

## Build instructions

You can create a wheel file by following the below steps

* Download or clone this repository.
* Run the below commands to create the package and install using pip.

```bash
python setup.py sdist bdist_wheel
pip install .
```

## Dependencies

The following packages need to be uploaded to the Azure Automation Account:

* pytz==2021.1

## Utilities

### VM Power Schedule

This utility allows to schedule a power on/off cycle by setting tags on VM instance type resources.

The power cycle will be run if the VM instance is in the correct state, that is if it needs to be powered on, it will
run if the instance is in `VM deallocated` or `VM stopped` statuses and if it needs to be powered off, it will run if
the instance is in `VM running` status.

If the VM instance is outside the time range and its status is `VM running` it will be powered off.

You can setup an hourly schedule basis, so it will check every hour for the correct power status of all VMs in the
subscription.

#### Tags implemented

|Tag name|Value|Default|Example|Description|
|--------|-----|-------|-------|-----------|
|VMPowerOn|number|-|23|Set the hour in which the VM should be powered ON|
|VMPowerOff|number|-|4|Set the hour in which the VM should be powered OFF|
|VMPowerDays|string|1,2,3,4|1,3,5,7|Set the days (separated by `commas`, `pipes` , `dashes` or `spaces`) in which the action should be performed|
|VMPowerSkip|any|1|-|Skip the VM while this tag is set|

#### Power transitions implemented

|Between time range|Initial Status|Final status|Description|
|:------------------:|--------------|------------|-----------|
|Yes|VM deallocated|VM running|You'd be billed for the instance|
|Yes|VM stopped|VM running|You'd be billed for the instance|
|No|VM running|VM deallocated|You wouldn't be billed for the instance|

**Please note that a time range between two days won't trigger any action if the scheduled days don't match.**

#### Example usage

The first step is to upload the utilities package and dependencies to Python packages (under Shared Resources) in the
Azure Automation Account.

The next step is to create a **Python 3** Runbook with the following code (using default values):

```python
from azure_runbook_util import vm_ops

vm_power_schedule = vm_ops.VmPowerSchedule()
vm_power_schedule.run()
```

Or using custom values:

```python
from azure_runbook_util import vm_ops

vm_power_tags = vm_ops.VmPowerTags(
    on="CustomTagOn",
    off="CustomTagOff",
    skip="CustomTagSkip",
    days="CustomTagDays",
)
vm_power_schedule = vm_ops.VmPowerSchedule(
  power_tags=vm_power_tags,  # An instance of VmPowerTags that holds the name of the tags to lookup
  debug=True, # Set logging level to DEBUG
  dry_run=True, # Perform a trial run with no changes made
  wait_for_action=True # Set to True to perform synchronous power cycle actions
)
vm_power_schedule.run()
```

## Development

In order to develop your own implementation, you will need:

* Install and configure the Azure Automation python emulated assets
  from https://github.com/azureautomation/python_emulated_assets.
* Install the requirements