#!/usr/bin/env python3
from pandas.core.indexes.range import RangeIndex
import numpy as np
import h5py
def append_hdf5(dataframe, hdf5, user_id, schema=None, source=None):
    if not (schema or source):
        raise ValueError('schema or source key-word argument must be supplied')

    if not source:
        source = shema.name

    h5_data_path = user_id + '/' + source
    if not h5_data_path in hdf5:
        hdf5.create_group(h5_data_path)

    if type(dataframe.index) != RangeIndex:
        dataframe.reset_index(level=0, inplace=True)

    for col in dataframe.keys():
        h5_col_path = h5_data_path + '/' + col
        col_len = len(dataframe[col])
        col_dtype = dataframe[col].dtype
        if col_dtype == np.dtype('O'):
            col_dtype = h5py.special_dtype(vlen=str)

        if col in hdf5[h5_data_path]:
            hdf5[h5_col_path].resize(hdf5.shape[0]+col_len, axis=0)
            hdf5[h5_col_path][-col_len:] = dataframe[col]
        else:
            hdf5[h5_data_path].create_dataset(col, data=dataframe[col], maxshape=(None,), dtype=col_dtype)

