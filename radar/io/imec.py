#!/usr/bin/env python3
import pandas as pd
import numpy as np
import tables
from .hdf5 import open_project
from collections import OrderedDict as od

IMEC_TABLE_ACC = od((
    ('value.time', tables.Int64Col()),
    ('value.x', tables.Float32Col()),
    ('value.y', tables.Float32Col()),
    ('value.z', tables.Float32Col()),
))
IMEC_TABLE_BATTERY = od((
    ('value.time', tables.Int64Col()),
    ('value.charge', tables.Float32Col()),
))
IMEC_TABLE_ECG = od((
    ('value.time', tables.Int64Col()),
    ('value.ecg', tables.Float32Col()),
    ('value.emg', tables.Float32Col()),
    ('value.gsr_1', tables.Float32Col()),
    ('value.gsr_2', tables.Float32Col()),
))
IMEC_TABLE_PIE = od((
    ('value.time', tables.Int64Col()),
    ('value.pie', tables.Float32Col()),
))
IMEC_TABLE_TEMP = ((
    ('value.time', tables.Int64Col()),
    ('value.temperature', tables.Float32Col()),
))
IMEC_TABLES = od((
    'imec_acceleration', (IMEC_TABLE_ACC, od((('value.time', '<M8[ns]'),
                                              ('value.x', '<f4'),
                                              ('value.y', '<f4'),
                                              ('value.z', '<f4')))),
    'imec_battery', (IMEC_TABLE_BATTERY, od((('value.time', '<M8[ns]'),
                                             ('value.charge', '<f4')))),
    'imec_electrodes', (IMEC_TABLE_ECG, od((('value.time', '<M8[ns]'),
                                            ('value.ecg', '<f4'),
                                            ('value.emg', '<f4'),
                                            ('value.gsr_1', '<f4'),
                                            ('value.gsr_2', '<f4')))),
    'imec_pie', (IMEC_TABLE_PIE, od((('value.time', '<M8[ns]'),
                                     ('value.pie', '<f4')))),
    'imec_temp', (IMEC_TABLE_TEMP, od((('value.time', '<M8[ns]'),
                                       ('value.temperature', '<f4'))))
))

IMEC_DATA_NAMES = {'imec_acceleration': ['ACC-X', 'ACC-Y', 'ACC-Z'],
                   'imec_battery': ['Battery'],
                   'imec_electrodes': ['ECG', 'EMG', 'GSR-1', 'GSR-2'],
                   'imec_pie': ['PIE'],
                   'imec_temp': ['Temp']}

def make_tables(target_hdf, target_where):
    out_dict = {}
    for title, table in IMEC_TABLES.items():
        print(title)
        print(target_where)
        out_dict[title] = target_hdf.create_radar_table(
            where=target_where, name=title, description=table[0], title=title)
        for k, v in table[1].items():
            setattr(out_dict[title].attrs, k, v)
        setattr(out_dict[title].attrs, 'NAME', title)
        setattr(out_dict[title].attrs, 'RADAR_TYPE', 'DATA')
    return out_dict

def data_generator(table, cols=None, batch_size=None):
    total_len = len(table)
    if batch_size is None:
        batch_size = table.chunkshape[0]
    i = 0
    while i < total_len:
        yield table[i:i+batch_size][cols]
        i += batch_size

def transfer_hdf(imec_hdf, target_hdf, target_where='', batch_size=None,
                 start_datetime=None):
    def get_freq(signal, name):
        return float(getattr(getattr(signal, name)._v_attrs, '#Freq'))

    def make_time_idx(inv_freq_ns, i, length):
        run_time = pd.Timedelta(int(inv_freq_ns*i))
        idx = pd.to_timedelta(np.tile(inv_freq_ns, length).cumsum()) + \
                start_datetime + run_time
        return idx

    def append_tab(outtab, data_names, col_names):
        i = 0
        freq = get_freq(signal, data_names[0])
        inv_freq_ns = (1/freq)*10**9
        col_gens = [data_generator(getattr(signal, name).Data,
                                   batch_size=batch_size) for name in data_names]
        for cols in zip(*col_gens):
            print(i)
            time_col = make_time_idx(inv_freq_ns, i, len(cols[0][0]))
            df_dict = od([(name, data[0]) for name, data
                          in zip(col_names, cols)])

            df_dict['time'] = time_col
            df = pd.DataFrame(df_dict)
            outtab.append(df.to_records(index=False))
            i += len(cols[0][0])

    if not isinstance(imec_hdf, tables.File):
        imec_hdf = open_project(imec_hdf, 'r')

    if isinstance(target_hdf, tables.Group):
        target_where = '/'.join([target_hdf._v_pathname, target_where])
        target_hdf = target_hdf._v_file
    elif isinstance(target_hdf, str):
        target_hdf = open_project(target_hdf, 'a')

    if start_datetime is None:
        dt_string = getattr(imec_hdf.root.Devices.Radar._v_attrs, '#DateTime')
        dt_string = dt_string.decode('utf-8')
        start_datetime = pd.to_datetime(dt_string)

    target_tables = make_tables(target_hdf, target_where)
    signal = imec_hdf.root.Devices.Radar.Signal

    for modality in IMEC_TABLES:
        print(modality)
        append_tab(target_tables[modality],
                   IMEC_DATA_NAMES[modality],
                   set(IMEC_TABLES[modality][1].keys()).difference(['time']))
