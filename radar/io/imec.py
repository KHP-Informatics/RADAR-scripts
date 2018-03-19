#!/usr/bin/env python3
import pandas as pd
import tables

IMEC_TABLE_ACC = {
    'x': tables.Float32Col(),
    'y': tables.Float32Col(),
    'z': tables.Float32Col(),
}
IMEC_TABLE_BATTERY = {
    'charge': tables.Float32Col(),
}
IMEC_TABLE_ECG = {}
IMEC_TABLE_EMG = {}
IMEC_TABLE_GSR = {}
IMEC_TABLE_PIE = {}
IMEC_TABLE_TEMP = {}

def make_tables(target_hdf, target_where):
    imec_tables = {
        'imec_acceleration': IMEC_TABLE_ACC,
        'imec_battery': IMEC_TABLE_BATTERY,
        'imec_ecg': IMEC_TABLE_ECG,
        'imec_emg': IMEC_TABLE_EMG,
        'imec_gsr': IMEC_TABLE_GSR,
        'imec_pie': IMEC_TABLE_PIE,
        'imec_temp': IMEC_TABLE_TEMP,
    }
    for title, table in tables.items():
        target_hdf.create_table()


def data_generator(table, cols=None, batch_size=None):
    total_len = len(table)
    if batch_size is None:
        batch_size = table.chunkshape[0]
    i = 0
    while i < total_len:
        yield table[i:i+batch_size][cols]
        i += batch_size

def hdf_to_dataframes(imec_path):
    hdf = tables.open_file(imec_path, 'r')
    dt_string = getattr(imec_h5.root.Devices.Radar._v_attrs, '#DateTime')
    dt_string = dt_string.decode('utf-8')
    start_datetime = pd.to_datetime(dt_string)


def transfer_hdf(imec_hdf, target_hdf, target_where='', batch_size=):
    if not isinstance(imec_hdf, tables.File):
        imec_hdf = tables.open_file(imec_hdf, 'r')

    if isinstance(target_hdf, tables.Group):
        target_where = '/'.join(target_hdf._v_pathname, target_where)
        target_hdf = target_hdf._v_file

    
