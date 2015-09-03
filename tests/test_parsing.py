from unittest import TestCase
import pandas as pd
from pandas.util.testing import assert_frame_equal

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


class TestDateParsing(TestCase):

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


class TestParseFile(TestCase):

    def setUp(self):
        tempdir = tempfile.gettempdir()
        filename = 'tfl_api_line_mode_status_tube_2015-02-24_12:03:14.json'
        self.filepath = os.path.join(tempdir, filename)
        self.file_datetime = pd.datetime(2015, 2, 24, 12, 3, 14)
        self.empty_df = pd.DataFrame({l: None for l in lines}, index=[self.file_datetime])

    def tearDown(self):
        try:
            os.unlink(self.filepath)
        except FileNotFoundError:
            pass

    def test_empty_file(self):
        with open(self.filepath, "w") as f:
            f.write('')
        result = parsing.parse_file(self.filepath)
        self.assertTrue(result.equals(self.empty_df))
        return

    def test_single_line(self):
        with open(self.filepath, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]
            """
            f.write(disruption)
        result = parsing.parse_file(self.filepath)
        line_values = self.empty_df
        line_values['bakerloo'] = 6
        assert_frame_equal(result, line_values)
        return

    def test_multiple_statuses_for_single_line(self):
        with open(self.filepath, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"},
                                                {"statusSeverity":10, "statusSeverityDescription":"Good Service"}]}]
            """
            f.write(disruption)
        result = parsing.parse_file(self.filepath)
        line_values = self.empty_df
        line_values['bakerloo'] = 6
        assert_frame_equal(result, line_values)
        return

    def test_multiple_statuses_reverse_order(self):
        with open(self.filepath, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":10, "statusSeverityDescription":"Good Service"},
                                                {"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]
            """
            f.write(disruption)
        result = parsing.parse_file(self.filepath)
        line_values = self.empty_df
        line_values['bakerloo'] = 6
        assert_frame_equal(result, line_values)
        return

    def test_multiple_lines(self):
        with open(self.filepath, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "circle", "lineStatuses":[{"statusSeverity":10, "statusSeverityDescription":"Good Service"}]}]
            """
            f.write(disruption)
        result = parsing.parse_file(self.filepath)
        line_values = self.empty_df
        line_values['bakerloo'] = 6
        line_values['circle'] = 10
        assert_frame_equal(result, line_values)
        return
