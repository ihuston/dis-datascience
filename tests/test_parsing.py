from unittest import TestCase

from dis_ds import parsing


class TestStatusSeverities(TestCase):

    def test_empty_file(self):
        empty_file = ""
        result = parsing.get_status_severities(empty_file)

        self.assertEqual(result, {})
        return

