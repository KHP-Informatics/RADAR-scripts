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

def read_csv_folder_type(path, extension='.csv', data_type='android_battery_level', **kwargs):
    shared_argu = {'parse_dates': ['value.time', 'value.timeReceived'],
                   'date_parser': parse_date,
                   'sort': ['value.time']}

    argu = {'android_battery_level': {
                'dtype': {
                    'value.batteryLevel': np.float64,
                    'value.isPlugged': np.bool_,
                    'value.status': str 
                    },
                'usecols': [3, 4, 5, 6, 7],
                },
            'android_acceleration':  {
                'dtype': {
                    'value.x': np.float64,
                    'value.y': np.float64,
                    'value.z': np.float64
                    },
                'usecols': [3, 4, 5, 6, 7],
                },
            'android_bluetooth_devices': {
                'dtype': {
                    'value.pairedDevices': np.int_,
                    'value.nearbyDevices': np.int_,
                    'value.bluetoothEnabled': np.bool_
                    },
                'usecols' : [3, 4, 5, 6, 7]
                },
            'android_call': {
                'dtype': {
                    'value.duration': np.float64,
                    'value.target': str,
                    'value.type': str,
                    'value.targetIsContact': np.bool_,
                    'value.targetIsNonNumberic': np.bool_,
                    'value.targetLength': np.int_
                    },
                'usecols': [3, 4, 5, 6, 7, 8, 9, 10]
                },
            'android_contacts': {
                'dtype': {
                    'value.contactsAdded': np.int_,
                    'value.contactsRemoved': np.int_,
                    'value.contacts': np.int_
                    },
                'usecols': [3, 4, 5, 6, 7]
                },
            'android_gyroscope': {
                'dtype': {
                    'value.x': np.float64,
                    'value.y': np.float64,
                    'value.z': np.float64
                    },
                'usecols': [3, 4, 5, 6, 7]
                },
            'android_light': {
                'dtype': {
                    'value.light': np.float64
                    },
                'usecols': [3, 4, 5]
                },
            'android_magnetic_field': {
                'dtype': {
                    'value.x': np.float64,
                    'value.y': np.float64,
                    'value.z': np.float64
                    },
                'usecols': [3, 4, 5, 6, 7]
                },
            'android_relative_location': {
                'dtypes': {
                    'value.provider': str,
                    'value.latitude': np.float64,
                    'value.longitude': np.float64,
                    'value.altitude': np.float64,
                    'value.accuracy': np.float64,
                    'value.speed': np.float64,
                    'value.bearing': np.float64
                    },
                'usecols': [3, 4, 5, 6, 7, 8, 9, 10, 11]
                },
            'android_sms': {
                'dtypes': {
                    'value.target': str,
                    'value.type': str,
                    'value.length': np.int_,
                    'value.targetIsContact': np.bool_,
                    'value.targetIsNonNumeric': np.bool_,
                    'value.targetLength': np.int_
                    },
                'usecols': [3, 4, 5, 6, 7, 8, 9, 10]
                },
            'android_sms_unread': {
                'dtypes': {
                    'value.unreadSms': np.int_
                    },
                'usecols': [3, 4, 5]
                },
            'android_step_count': {
                'dtypes': {
                    'value.steps': np.int_
                    },
                'usecols': [3, 4, 5]
                },
            'android_usage_event': {
                'dtypes': {
                    'value.packageName': str,
                    'value.categoryName': str,
                    '"value.categoryNameFetchTime"': np.float64,
                    'value.eventType': str
                    },
                'usecols': [3, 4, 5, 6, 7, 8]
                },
            'android_user_interaction': {
                'dtypes': {
                    'value.interactionState': str
                    },
                'usecols': [3, 4, 5]
                }
    }[data_type]
    argu.update(shared_argu)

    return read_csv_folder(path, extension, **argu, **kwargs)

