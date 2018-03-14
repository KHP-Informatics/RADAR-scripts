#!/usr/bin/env python3
import pandas as pd
import numpy as np
import glob, os, sys
import csv

def write_csv(arr, fname='', fieldnames='', **kwargs):
    f = open(fname, 'w') if fname else sys.stdout
    writer = csv.writer(f, **kwargs)
    if fieldnames:
        writer.writerow(fieldnames)
    for row in arr:
        writer.writerow(row)
    if f is not sys.stdout:
        f.close()

def read_files(files, sort='value.time', index='value.time', **kwargs):
    df = pd.concat(pd.read_csv(f, **kwargs) for f in files)
    if sort:
        df = df.sort_values(by=sort)
    if index:
        df = df.set_index(index)
    return df

def read_folder(path, extension='.csv', sort=False, **kwargs):
    files = glob.glob(os.path.join(path, '*' + extension))
    if files:
        return read_csv_files(files, sort, **kwargs)
    print('No files found in', path)
    return

def parse_date(timestamp):
    return pd.Timestamp.fromtimestamp(float(timestamp))

def read_csv_folder_type(path, data_type='android_phone_battery_level',
                         extension='.csv', **kwargs):
    shared_argu = {'parse_dates': ['value.time', 'value.timeReceived'],
                   'date_parser': parse_date,
                   'sort': ['value.time']}

    argu_dict = {
        'android_phone_battery_level': {
            'dtype': {
                'value.batteryLevel': np.float64,
                'value.isPlugged': np.bool_,
                'value.status': str,
            },
            'usecols': [3, 4, 5, 6, 7],
        },
        'android_phone_acceleration':  {
            'dtype': {
                'value.x': np.float64,
                'value.y': np.float64,
                'value.z': np.float64,
            },
            'usecols': [3, 4, 5, 6, 7],
        },
        'android_phone_bluetooth_devices': {
            'dtype': {
                'value.pairedDevices': np.int_,
                'value.nearbyDevices': np.int_,
                'value.bluetoothEnabled': np.bool_
            },
            'usecols' : [3, 4, 5, 6, 7],
        },
        'android_phone_call': {
            'dtype': {
                'value.duration': np.float64,
                'value.target': str,
                'value.type': str,
                'value.targetIsContact': np.bool_,
                'value.targetIsNonNumberic': np.bool_,
                'value.targetLength': np.int_,
            },
            'usecols': [3, 4, 5, 6, 7, 8, 9, 10],
        },
        'android_phone_contacts': {
            'dtype': {
                'value.contactsAdded': np.int_,
                'value.contactsRemoved': np.int_,
                'value.contacts': np.int_,
            },
            'usecols': [3, 4, 5, 6, 7],
        },
        'android_phone_gyroscope': {
            'dtype': {
                'value.x': np.float64,
                'value.y': np.float64,
                'value.z': np.float64,
            },
            'usecols': [3, 4, 5, 6, 7],
        },
        'android_phone_light': {
            'dtype': {
                'value.light': np.float64
            },
            'usecols': [3, 4, 5]
        },
        'android_phone_magnetic_field': {
            'dtype': {
                'value.x': np.float64,
                'value.y': np.float64,
                'value.z': np.float64,
            },
            'usecols': [3, 4, 5, 6, 7],
        },
        'android_phone_relative_location': {
            'dtype': {
                'value.provider': str,
                'value.latitude': np.float64,
                'value.longitude': np.float64,
                'value.altitude': np.float64,
                'value.accuracy': np.float64,
                'value.speed': np.float64,
                'value.bearing': np.float64,
            },
            'usecols': [3, 4, 5, 6, 7, 8, 9, 10, 11],
        },
        'android_phone_sms': {
            'dtype': {
                'value.target': str,
                'value.type': str,
                'value.length': np.int_,
                'value.targetIsContact': np.bool_,
                'value.targetIsNonNumeric': np.bool_,
                'value.targetLength': np.int_,
            },
            'usecols': [3, 4, 5, 6, 7, 8, 9, 10],
        },
        'android_phone_sms_unread': {
            'dtype': {
                'value.unreadSms': np.int_,
                },
            'usecols': [3, 4, 5],
        },
        'android_phone_step_count': {
            'dtype': {
                'value.steps': np.int_,
            },
            'usecols': [3, 4, 5]
        },
        'android_phone_usage_event': {
            'dtype': {
                'value.packageName': str,
                'value.categoryName': str,
                '"value.categoryNameFetchTime"': np.float64,
                'value.eventType': str,
            },
            'usecols': [3, 4, 5, 6, 7, 8],
        },
        'android_phone_user_interaction': {
            'dtype': {
                'value.interactionState': str,
            },
            'usecols': [3, 4, 5],
        },
        'android_empatica_e4_acceleration': {
            'dtype': {
                'value.x': np.float64,
                'value.y': np.float64,
                'value.z': np.float64,
            },
            'usecols': [2, 3, 4, 5, 6],
        },
        'android_empatica_e4_battery_level': {
            'dtype': {
                'value.batteryLevel': np.float64,
            },
            'usecols': [2, 3, 4],
        },
        'android_empatica_e4_blood_volume_pulse': {
            'dtype': {
                'value.bloodVolumePulse': np.float64,
            },
            'usecols': [2, 3, 4],
        },
        'android_empatica_e4_electrodermal_activity': {
            'dtype': {
                '"value.electroDermalActivity"': np.float64,
            },
            'usecols': [2, 3, 4],
        },
        'android_empatica_e4_inter_beat_interval': {
            'dtype': {
                'value.interBeatInterval': np.float64,
            },
            'usecols': [2, 3, 4],
        },
        'android_empatica_e4_empatica_e4_temperature': {
            'dtype': {
                'value.temperature': np.float64,
            },
            'usecols': [2, 3, 4],
        },
        'android_eeg_sync_pulse': {
            'dtype': {
                'value.width': np.float64,
                'value.delay': np.float64,
            },
            'usecols': [2, 3, 4, 5],
        },
    }[data_type]

    shared_argu.update(argu_dict)
    if len(kwargs) > 1:
        shared_argu.update(kwargs)
    return read_csv_folder(path, extension, **shared_argu)

