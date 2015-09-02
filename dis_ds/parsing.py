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
