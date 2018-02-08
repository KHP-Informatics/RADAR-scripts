#!/usr/bin/env python3
import pandas as pd
import numpy as np
import glob
import os

def read_csv_files(files, sort=False, **kwargs):
    df = pd.concat(pd.read_csv(f, **kwargs) for f in files)
    if sort:
        df = df.sort_values(by=sort)
    return df

def read_csv_folder(path, extension='.csv', sort=False, **kwargs):
    files = glob.glob(os.path.join(path, '*' + extension))
    return read_csv_files(files, sort, **kwargs)

def parse_date(timestamp):
    return pd.Timestamp.fromtimestamp(float(timestamp))

def read_csv_folder_type(path, extension='.csv', data_type='battery_level', **kwargs):
    argu = {'battery_level': {'parse_dates': ['value.time', 'value.timeReceived'],
                              'date_parser': parse_date,
                              'dtype': {'value.batteryLevel': np.float64,
                                   'value.isPlugged': np.bool_,
                                   'value.status': str },
                              'usecols': [3, 4, 5, 6, 7],
                              'sort': ['value.time'],
                             },
            'acceleration':  {'parse_dates': ['value.time', 'value.timeReceived'],
                              'date_parser': parse_date,
                              'dtype': {'value.x': np.float64,
                                        'value.y': np.float64,
                                        'value.z': np.float64},
                              'usecols': [3, 4, 5, 6, 7],
                              'sort': ['value.time'],
                              }
    }[data_type]

    return read_csv_folder(path, extension, **argu, **kwargs)

