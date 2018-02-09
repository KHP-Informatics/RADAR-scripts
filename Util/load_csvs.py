#!/usr/bin/env python3
import pandas as pd
import numpy as np
import glob
import os

def read_csv_files(files, sort='value.time', index='value.time', **kwargs):
    df = pd.concat(pd.read_csv(f, **kwargs) for f in files)
    if sort:
        df = df.sort_values(by=sort)
    if index:
        df = df.set_index(index)
    return df

def read_csv_folder(path, extension='.csv', sort=False, **kwargs):
    files = glob.glob(os.path.join(path, '*' + extension))
    return read_csv_files(files, sort, **kwargs)

def parse_date(timestamp):
    return pd.Timestamp.fromtimestamp(float(timestamp))

def read_csv_folder_type(path, extension='.csv', data_type='battery_level', **kwargs):
    shared_argu = {'parse_dates': ['value.time', 'value.timeReceived'],
                   'date_parser': parse_date,
                   'sort': ['value.time']}

    argu = {'battery_level': {'dtype': {'value.batteryLevel': np.float64,
                                   'value.isPlugged': np.bool_,
                                   'value.status': str },
                              'usecols': [3, 4, 5, 6, 7],
                             },
            'acceleration':  {'dtype': {'value.x': np.float64,
                                        'value.y': np.float64,
                                        'value.z': np.float64},
                              'usecols': [3, 4, 5, 6, 7],
                             }
    }[data_type]
    argu.update(shared_argu)

    return read_csv_folder(path, extension, **argu, **kwargs)

