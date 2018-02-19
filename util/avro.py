#!/usr/bin/env python3
from avro import schema
from util._schema_header import *

class RadarSchema():
    def __init__(self, json):
        self.schema = schema.Parse(json)

    def get_col_info(self, func=None, keys=()):
        """
        Gets field info from field[].type.field[key] where keys are given as
        an argument.
        To get values from child keys, give multiple keys. For example,
        _get_col_info('name') returns the name of a data array,
        _get_col_info('type', 'type') returns the type because it is nested.
        Alternatively, a custom function may be supplied by the func argument.
        This will append the result of the function on the column.
        """
        def get_info_rec(col, *keys):
            if len(keys) > 1:
                return get_info_rec(col.props[keys[0]], *keys[1:])
            else:
                return col.props[keys[0]]
        if not func:
            func = get_info_rec
        return [func(col, *keys) for field in self.schema.fields
                                 for col in field.type.fields]

    def get_col_names(self,):
        return self.get_col_info(keys=['name'])

    def get_col_types(self,):
        def get_type(col):
            typeval = col.type.type
            if typeval == 'union':
                typelist = []
                for sch in col.type.schemas:
                    typelist.append(sch.type)
                return typelist
            else:
                return typeval
        return self.get_col_info(func=get_type)

    def get_col_numpy_types(self):
        def convert_type(data_type):
            if isinstance(data_type, list):
                return [convert_type(x) for x in data_type]
            else:
                return AVRO_NUMPY_TYPES[data_type]
        return [convert_type(x) for x in self.get_col_types()]

    def load_csv(self, csv_file, **kwargs):
        pass
    def load_csvs_folder(self, folder_path, **kwargs):
        pass
    def _infer_time(self,):
        return True
    infer_time_type = True;
    time_columns = [];
