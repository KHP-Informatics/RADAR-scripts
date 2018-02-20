#!/usr/bin/env python3
from avro import schema
import pandas as pd
import numpy as np
import glob, os
from util._schema_header import *

class RadarSchema():
    """
    A class for use with RADAR-base key-value pair schemas. Initialise with a
    json string representation of the schema.
    """

    INDEX = 'value.time'
    SORT = 'value.time'
    TIME_COLS = ['value.time', 'value.timeReceived']
    CSV_EXT = '.csv'
    usekeys = True

    class _FakeSchema(object):
        pass

    def __init__(self, json, values=False):
        """
        This class must be initiated with a json string representation of a
        RADAR-base schema.
        It is possible to provide a values only schema by setting values=True,
        but it will not load key column data.
        """
        if values:
            self.schema = self._FakeSchema()
            self.schema.fields = [self._FakeSchema()]
            self.schema.fields[0].type = schema.Parse(json)
            self.schema.fields[0].name = 'value'
        else:
            self.schema = schema.Parse(json)

    def get_col_info(self, func=None, *args):
        """
        Values from schema columns and their parent fields can be retrieved by
        a given function.
        """
        return [func(col, field, *args) for field in self.schema.fields
                                        for col in field.type.fields]

    def get_col_info_by_key(self, *keys):
        """
        Gets values from a schema column by its dict key. Multiple keys can be
        supplied for nested values.
        """
        def get_info_rec(col, par, *keys):
            if len(keys) > 1:
                return get_info_rec(col.props[keys[0]], par, *keys[1:])
            else:
                return col.props[keys[0]]
        return self.get_col_info(get_info_rec, *keys)

    def get_col_names(self,):
        """
        Returns an array of column names for the csv created by the schema
        """
        def get_name(col, parent):
            return parent.name + '.' + col.name
        return self.get_col_info(func=get_name)

    def get_col_types(self,):
        """
        Returns an array of strings naming Avro datatypes for each csv column
        created by the schema
        """
        def get_type(col, *args):
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

    def load_csvs(self, csv_filepath_list, **kwargs):
        argdict = self._get_schema_kwargs()
        if kwargs:
            argdict = argdict.update(kwargs)
        df = pd.concat(pd.read_csv(f, **argdict) for f in csv_filepath_list)
        if self.SORT:
            df = df.sort_values(by=self.SORT)
        if self.INDEX:
            df = df.set_index(self.INDEX)
        return df

    def load_csv_folder(self, folder_path, **kwargs):
        files = glob.glob(os.path.join(folder_path, '*' + self.CSV_EXT))
        if files:
            return self.load_csvs(files, **kwargs)
        else:
            raise IOError('No CSV files found in given path')

    def _get_schema_kwargs(self):
        # Some of this function (ignoring keys, etc) should be moved elsewhere
        argdict = {}
        cols = self.get_col_names()
        argdict['dtype'] = {col:dtype for col, dtype in
                            zip(cols, self.get_col_numpy_types())
                            if col not in self.TIME_COLS}
        if not self.usekeys:
            argdict['usecols'] = [k for k in cols if k[0:4] != 'key.']
            delkeys = [k for k in cols if k[0:4] == 'key.']
            for k in delkeys:
                if k in argdict['dtype']:
                    del argdict['dtype'][k]
        else:
            argdict['usecols'] = cols

        if self.TIME_COLS:
            argdict['parse_dates'] = [col for col in cols if col in
                                      self.TIME_COLS]
            argdict['date_parser'] = self._parse_date

        return argdict

    def _infer_time(self,):
        raise NotImplementedError

    def _parse_date(self, timestamp):
        return pd.Timestamp.fromtimestamp(float(timestamp))

