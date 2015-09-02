# Parsing module for dis
#
import os
import datetime
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
    if os.stat(filepath).st_size != 0:
        df = pd.read_json(filepath)
        for index, line in df.iterrows():
            line_id = line['id']
            severity = line['lineStatuses'][0]['statusSeverity']
            line_values[line_id] = severity
    return pd.DataFrame(line_values, index=[datetime])
