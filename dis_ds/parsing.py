# Parsing module for dis
#
import os
import datetime
import boto
import pandas as pd

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


def get_status_severities(file):
    if file == "":
        return {}

    df = pd.read_json(file)
    severities = {}
    for line in df['lineStatuses']:
        for status in line:
            severities[status['statusSeverity']] = status['statusSeverityDescription']
    return severities


def get_severities_from_files(filenames):
    severities = {}
    for file in filenames:
        result = get_status_severities(file)
        severities.update(result)

    return severities


def get_datetime_from_filename(filepath):
    _, filename = os.path.split(filepath)
    dt = datetime.datetime.strptime(filename, 'tfl_api_line_mode_status_tube_%Y-%m-%d_%H:%M:%S.json')
    return dt


def parse_file(filepath):
    datetime = get_datetime_from_filename(filepath)
    line_values = {l: None for l in lines}
    try:
        df = pd.read_json(filepath)
    except (IOError, ValueError, boto.exception.S3ResponseError):
        # TODO Add logging of errors
        pass
    else:
        for index, line in df.iterrows():
            line_id = line['id']
            severities = [line_status['statusSeverity'] for line_status in line['lineStatuses']]
            line_values[line_id] = min(severities)
    return pd.DataFrame(line_values, index=[datetime]).astype(float)


def parse_file_list(file_list):
    result_list = [parse_file(file) for file in file_list]
    result_df = pd.concat(result_list)
    return result_df
