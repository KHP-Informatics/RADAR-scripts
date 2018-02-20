#!/usr/bin/env python3
from avro import schema
import pandas as pd
import numpy as np
from util._schema_header import *

class RadarSchema():
    def __init__(self, json):
        """
        This class must be initiated with a json string representation of a
        RADAR-base schema
        """
        self.schema = schema.Parse(json)

    def get_col_info(self, func=None, keys=(), parent_name=False):
        """
        Gets field info from field[].type.field[key] where keys are given as
        an argument.
        To get values from child keys, give multiple keys. For example,
        get_col_info(keys=['name']) returns the name of a data array,
        get_col_info(keys=['type', 'type']) returns the type because it is nested.
        Alternatively, a custom function may be supplied by the func argument.
        This will append the result of the function on the column.
        """
        def get_info_rec(col, par, *keys):
            if len(keys) > 1:
                return get_info_rec(col.props[keys[0]], *keys[1:])
            else:
                return col.props[keys[0]]
        if not func:
            func = get_info_rec

        if parent_name:
            return [field.name + '.' + func(col, *keys)
                    for field in self.schema.fields
                    for col in field.type.fields]
        else:
            return [func(col, field, *keys) for field in self.schema.fields
                                            for col in field.type.fields]

    def get_col_names(self,):
        """
        Returns an array of column names for the csv created by the schema
        """
        return self.get_col_info(keys=['name'], parent_name=True)

    def get_col_types(self,):
        """
        Returns an array of strings naming Avro datatypes for each csv column
        created by the schema
        """
        def get_type(col):
            typeval = col.type.type
            if typeval == 'union':
                return [sch.type for sch in col.type.schemas]
            else:
                return typeval

        return self.get_col_info(func=get_type)

    def get_col_numpy_types(self):
        """
        Returns an array of the equivilent numpy datatypes for the csv file for
        the schema
        """
        def convert_type(data_type):
            if isinstance(data_type, list):
                dtype = [convert_type(x) for x in data_type if x != 'null']
                if len(dtype) == 1:
                    return dtype[0]
                else:
                    return dtype
            else:
                return AVRO_NUMPY_TYPES[data_type]
        return [convert_type(x) for x in self.get_col_types()]

    def load_csv(self, csv_file_path, **kwargs):
        argdict = self.get_schema_kwargs()
        if kwargs:
            argdict = argdict.update(kwargs)
        df = pd.read_csv(csv_file_path, **argdict)
        if self.sort:
            df = df.sort_values(by=self.sort)
        if self.index:
            df = df.set_index(self.index)
        return df

    def load_multiple_csv(self, csv_filepath_array, **kwargs):
        argdict = self.get_schema_kwargs()
        if kwargs:
            argdict = argdict.update(kwargs)
        df = pd.concat(pd.read_csv(f, **argdict) for f in csv_filepath_array)
        if self.sort:
            df = df.sort_values(by=self.sort)
        if self.index:
            df = df.set_index(self.index)
        return df

    def load_csv_folder(self, folder_path, **kwargs):
        files = glob.glob(os.path.join(path, '*', + extension))
        if files:
            return self.load_multiple_csv(files, **kwargs)
        else:
            raise IOError('No CSV files found in given path')

    def get_schema_kwargs(self):
        # Some of this function (ignoring keys, etc) should be moved elsewhere
        argdict = {}
        cols = self.get_col_names()
        argdict['dtype'] = {col:dtype for col, dtype in
                            zip(cols, self.get_col_numpy_types())
                            if col not in self.time_columns}
        if not self.usekeys:
            argdict['usecols'] = [k for k in cols if k[0:4] != 'key.']
            delkeys = [k for k in cols if k[0:4] == 'key.']
            for k in delkeys:
                if k in argdict['dtype']:
                    del argdict['dtype'][k]
        else:
            argdict['usecols'] = cols

        if self.time_columns:
            argdict['parse_dates'] = [col for col in cols if col in
                                      self.time_columns]
            argdict['date_parser'] = self._parse_date

        return argdict

    def _infer_time(self,):
        raise NotImplementedError

    def _parse_date(self, timestamp):
        return pd.Timestamp.fromtimestamp(float(timestamp))

    # infer_time_type = True;
    time_columns = ['value.time', 'value.timeReceived'];
    sort = 'value.time';
    index = 'value.time';
    usekeys = True;
