from unittest import TestCase
import pandas as pd

from dis_ds import parsing
import tempfile
import os

lines = ['bakerloo',
         'central',
         'circle',
         'district',
         'hammersmith-city',
         'jubilee',
         'metropolitan',
         'northern',
         'piccadilly',
         'victoria',
         'waterloo-city']


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

    def test_real_file(self):
        file = tempfile.NamedTemporaryFile(delete=False)
        file_name = file.name
        file.write(b'[{"lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]')
        file.close()
        result = parsing.get_status_severities(file_name)
        expected = {6: "Severe Delays"}
        self.assertEqual(expected, result)
        os.unlink(file_name)
        return

    def test_multiple_files(self):
        file1 = tempfile.NamedTemporaryFile(delete=False)
        file2 = tempfile.NamedTemporaryFile(delete=False)
        file_names = [file1.name, file2.name]
        file1.write(b'[{"lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]')
        file2.write(b'[{"lineStatuses":[{"statusSeverity":9, "statusSeverityDescription":"Minor Delays"}]}]')
        file1.close()
        file2.close()

        result = parsing.get_severities_from_files(file_names)
        expected = {6: "Severe Delays", 9: "Minor Delays"}
        self.assertEqual(expected, result)
        for fname in file_names:
            os.unlink(fname)
        return


class TestParseFile(TestCase):

    def test_empty_file(self):
        tempdir = tempfile.gettempdir()
        filename = 'tfl_api_line_mode_status_tube_2015-02-24_12:03:14.json'
        filepath = os.path.join(tempdir, filename)
        with open(filepath, "w") as f:
            f.write('')
        result = parsing.parse_file(filepath)
        this_datetime = pd.datetime(2015, 2, 24, 12, 3, 14)
        expected = pd.DataFrame({l: None for l in lines}, index=[this_datetime])
        self.assertTrue(result.equals(expected))
        return

    def test_parse_date(self):
        filename = 'tfl_api_line_mode_status_tube_2015-02-24_12:03:14.json'
        result = parsing.get_datetime_from_filename(filename)
        expected = pd.datetime(2015, 2, 24, 12, 3, 14)

        self.assertEqual(result, expected)
        return

    def test_parse_date_from_path(self):
        filename = '/tmp/tfl_api_line_mode_status_tube_2015-02-24_12:03:14.json'
        result = parsing.get_datetime_from_filename(filename)
        expected = pd.datetime(2015, 2, 24, 12, 3, 14)

        self.assertEqual(result, expected)
        return

    def test_single_line(self):
        tempdir = tempfile.gettempdir()
        filename = 'tfl_api_line_mode_status_tube_2015-02-24_12:03:14.json'
        filepath = os.path.join(tempdir, filename)
        with open(filepath, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]
            """
            f.write(disruption)
        result = parsing.parse_file(filepath)
        this_datetime = pd.datetime(2015, 2, 24, 12, 3, 14)
        line_values = {l: None for l in lines}
        line_values['bakerloo'] = 6
        expected = pd.DataFrame(line_values, index=[this_datetime])
        self.assertTrue(result.equals(expected))
        return

    def test_multiple_statuses_for_single_line(self):
        pass

