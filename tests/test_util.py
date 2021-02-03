import json
import unittest

from unittest_data_provider import data_provider

from azure_runbook_util import util


def times():
    return (
        (1, 2, 1, True),
        (1, 2, 2, False),
        (22, 1, 21, False),
        (22, 1, 0, True),
        (22, 1, 2, False)
    )


class TestUtil(unittest.TestCase):

    @data_provider(times)
    def test_time_in_range(self, start, end, hour, result):
        self.assertEqual(result, util.time_in_range(start, end, hour))

    def test_get_json(self):
        o = dict(id=1, name="test")

        self.assertEqual(json.dumps(o), util.get_json(o))


if __name__ == '__main__':
    unittest.main()
