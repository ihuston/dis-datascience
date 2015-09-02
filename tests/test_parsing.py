from unittest import TestCase

from dis_ds import parsing


class TestStatusSeverities(TestCase):

    def test_empty_file(self):
        empty_file = ""
        result = parsing.get_status_severities(empty_file)

        self.assertEqual(result, {})
        return

    def test_single_severity(self):
        single_severity_file = '[{"lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]'

        result = parsing.get_status_severities(single_severity_file)
        expected = {6: "Severe Delays"}
        self.assertEqual(expected, result)
        return

    def test_multiple_severity(self):
        multiple_severity_file = """
        [{"lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
         {"lineStatuses":[{"statusSeverity":10, "statusSeverityDescription":"Good Service"}]}]
        """

        result = parsing.get_status_severities(multiple_severity_file)
        expected = {6: 'Severe Delays', 10: 'Good Service'}
        self.assertEqual(expected, result)
        return

    def test_multiple_severities_for_a_single_line(self):
        multiple_severity_file = """
        [{"lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"},
                          {"statusSeverity":9, "statusSeverityDescription":"Minor Delays"}]}]
        """

        result = parsing.get_status_severities(multiple_severity_file)
        expected = {6: 'Severe Delays', 9: 'Minor Delays'}
        self.assertEqual(expected, result)
        return

