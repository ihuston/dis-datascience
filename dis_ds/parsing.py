# Parsing module for dis
#
import pandas as pd


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

