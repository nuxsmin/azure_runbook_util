import unittest
from unittest_data_provider import data_provider
from azure_runbook_util import vm_ops


def days_of_week():
    return (
        ("1 2 3 4 5 6 7", True),
        ("1,2,3,4,5,6,7", True),
        ("1;2;3;4;5;6;7", True),
        ("1-2-3-4-5-6-7", True),
        ("1|2|3|4|5|6|7", True),
    )


class TestVmPowerSchedule(unittest.TestCase):

    @data_provider(days_of_week)
    def test_is_scheduled(self, days, result):
        vm_power_schedule = vm_ops.VmPowerSchedule()

        self.assertEqual(result, vm_power_schedule.is_scheduled(days))

    def test_is_scheduled_wrong_string(self):
        days = "1234567"

        vm_power_schedule = vm_ops.VmPowerSchedule()

        self.assertEqual(False, vm_power_schedule.is_scheduled(days))


if __name__ == '__main__':
    unittest.main()
