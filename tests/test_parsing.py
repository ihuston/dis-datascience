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
        self.empty_df = pd.DataFrame({l: None for l in lines}, index=[self.file_datetime]).astype(float)

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
        line_values['bakerloo'] = 6.0
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
        line_values['bakerloo'] = 6.0
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
        line_values['bakerloo'] = 6.0
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
        line_values['bakerloo'] = 6.0
        line_values['circle'] = 10.0
        assert_frame_equal(result, line_values)
        return


class TestParseMultipleFiles(TestCase):

    def setUp(self):
        tempdir = tempfile.gettempdir()
        filename1 = 'tfl_api_line_mode_status_tube_2015-02-24_12:03:14.json'
        filename2 = 'tfl_api_line_mode_status_tube_2015-02-25_12:00:00.json'
        self.filepath1 = os.path.join(tempdir, filename1)
        self.file_datetime1 = pd.datetime(2015, 2, 24, 12, 3, 14)
        self.filepath2 = os.path.join(tempdir, filename2)
        self.file_datetime2 = pd.datetime(2015, 2, 25, 12, 0, 0)
        self.default_lines = pd.DataFrame({l: 6 for l in lines}, index=[self.file_datetime1, self.file_datetime2]).astype(float)

    def tearDown(self):
        try:
            os.unlink(self.filepath1)
            os.unlink(self.filepath2)
        except FileNotFoundError:
            pass

    def test_multiple_files(self):

        with open(self.filepath1, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "central", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "circle", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "district", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "hammersmith-city", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "jubilee", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "metropolitan", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "northern", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "piccadilly", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "victoria", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "waterloo-city", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]
            """

            f.write(disruption)
        with open(self.filepath2, "w") as f:
            disruption = """
            [{"id": "bakerloo", "lineStatuses":[{"statusSeverity":10, "statusSeverityDescription":"Good Service"}]},
             {"id": "central", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "circle", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "district", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "hammersmith-city", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "jubilee", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "metropolitan", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "northern", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "piccadilly", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "victoria", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]},
             {"id": "waterloo-city", "lineStatuses":[{"statusSeverity":6, "statusSeverityDescription":"Severe Delays"}]}]
            """
            f.write(disruption)
        result = parsing.parse_file_list([self.filepath1, self.filepath2])
        line_values = self.default_lines
        line_values.ix[1]['bakerloo'] = 10
        print('result = {}'.format(result.dtypes))
        print('line_values = {}'.format(line_values.dtypes))
        assert_frame_equal(result, line_values)

        return


class TestAWSParsing(TestCase):

    testfile = 's3://pivotal-london-dis/tfl_api_line_mode_status_tube_2015-02-24_11:51:45.json'

    def test_aws_connectivity(self):
        newfile = pd.read_json(self.testfile)
        assert newfile is not None

    def test_aws_parsing(self):
        parsed = parsing.parse_file(self.testfile)
        self.assertTrue(len(parsed.columns), 11)

    def test_missing_file(self):
        file_datetime = pd.datetime(2010, 2, 24, 11, 51, 45)
        empty_df = pd.DataFrame({l: None for l in lines}, index=[file_datetime]).astype(float)
        parsed = parsing.parse_file('s3://pivotal-london-dis/tfl_api_line_mode_status_tube_2010-02-24_11:51:45.json')
        assert_frame_equal(parsed, empty_df)
