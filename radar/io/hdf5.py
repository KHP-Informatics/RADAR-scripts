#!/usr/bin/env python3
import tables
import numpy as np
import pandas as pd
from radar.util.common import AVRO_HDF_TYPE
_FILTER = tables.Filters(complib='blosc:snappy', complevel=1, shuffle=True)

def open_project(filename, mode='r', title='', root_uep='/',
                 filters=_FILTER, **kwargs):
    """
    """
    if tables.file._FILE_OPEN_POLICY == 'strict':
        if filename in tables.file._open_files:
            raise ValueError('The file %s is already open', filename)
        else:
            for filehandle in \
            tables.file._open_files.get_handlers_by_name(filename):
                omode = filehandle.mode
                if mode == 'r' and omode != 'r':
                    raise ValueError(
                        'The file "%s" is already opened not in ',
                        'read-only mode', filename)
                elif mode in ('a', 'r+') and omode == 'r':
                    raise ValueError(
                        'The file "%s" is already opened in ',
                        'read-only mode. Can\'t open append mode.')
                elif mode == 'w':
                    raise ValueError(
                        'The file "%s" is already opened. Can\'t ',
                        'reopen in write mode', filename)
        return ProjectFile(filename, mode, title, root_uep, filters, **kwargs)

def _descr_from_schema(radar_schema):
    """ Generates a table description from a RADAR schema.
    Parameters
    _________
    radar_schema : RadarSchema object
        A RadarSchema object from util.avro.RadarSchema of this package

    Returns
    _______
    : tables.Description object
        A PyTables Description object generated from the given schema

    See Also
    ________
    tables.Description : The PyTables object that describes a HDF5 table.
    """
    classdict = {}
    names = radar_schema.get_col_names()
    dtypes = radar_schema.get_col_types()
    for name, dtype in zip(names, dtypes):
        classdict[name] = AVRO_HDF_TYPE[dtype]
    return tables.Description(classdict)

class ProjectFile(tables.File):
    """ HDF5 file for a RADAR project. Subclass of tables.File TODO
    Parameters
    __________
    See Also
    ________
    tables.File : For more information on the PyTables File object
    """

    def __init__(self, filename, mode='r', title='', root_uep='/',
                 filters=_FILTER, subprojects=[], **kwargs):
        super(ProjectFile, self).__init__(filename=filename, mode=mode, title=title,
                               root_uep=root_uep, filters=filters,
                               **kwargs)
        self.subprojects = subprojects

    def create_radar_table(self, where, name, description=None, title='',
                     filters=_FILTER, expectedrows=1000000,
                     chunkshape=None, byteorder=None,
                     createparents=True, obj=None):
        """ Create a new radar table
        Essentially a copy of tables.File.create_table()
        Parameters
        __________

        See also
        ________
        tables.File.create_table()
        """
        if obj is not None:
            if isinstance(obj, np.ndarray):
                pass
            elif isinstance(obj, pd.DataFrame):
                obj = obj.to_records()
            else:
                raise TypeError('Invalid obj type %r' %obj)
            descr, _ = tables.description.descr_from_dtype(obj.dtype)
            if (description is not None and
                tables.description.dtype_from_descr(description) != obj.dtype):
                raise TypeError('The description parameter is not consistent ',
                            'with the data object')
            description = descr
        parentnode = self._get_or_create_path(where, createparents)
        if description is None:
            raise ValueError('No description provided')
        tables.file._checkfilters(filters)

        ptobj = RadarTable(parentnode, name, description=description,
                           title=title, filters=filters,
                           expectedrows=expectedrows, chunkshape=chunkshape,
                           byteorder=byteorder)
        if obj is not None:
            ptobj.append(obj)

        return ptobj

    def create_table_schema(self, where, name, schema, createparents=True,
                            **kwargs):
        """ Create a new table based on a given schema TODO
        """
        raise NotImplementedError()
        description = schemafunc(schema)
        self.create_radar_table(where, name, description=description,
                                createparents=createparents, **kwargs)


    def save_dataframe(self, df, where, name, **kwargs):
        """Add a pandas dataframe to an entrypoint in the hdf5 file
        """
        df, attrib_types = _df_to_usable(df)
        table = self.create_radar_table(where, name, obj=df, **kwargs)
        for k, v in attrib_types.items():
            setattr(table.attrs, k, v)
        return table


class RadarTable(tables.Table):
    """ A Table object for RADAR data
    Parameters
    _________
    See also
    ________
    tables.Table : For more information on the PyTables Table object
    """
    def __init__(self, parentnode, name,
                filters=_FILTER, **kwargs):
        super(RadarTable, self).__init__(parentnode, name, filters=_FILTER, **kwargs)

    def insert_dataframe(self, df, attr=False):
        pass


def dataframe_description(df):
    descr = {}
    for col, dt in zip(df.columns, df.dtypes):
        if dt == 'O':
            # Object / string
            descr[col] = tables.StringCol(df[col].map(len).max())
        elif dt == 'bool':
            descr[col] = tables.BoolCol()
        elif dt == 'int32':
            descr[col] = tables.Int32Col()
        elif dt == 'int64':
            descr[col] = tables.Int64Col()
        elif dt == 'datetime64[ns]':
            descr[col] = tables.Int64Col()
        elif dt == 'float32':
            descr[col] = tables.Float32Col()
        elif dt == 'float64':
            descr[col] = tables.Float64Col()
        elif dt == 'bytes':
            descr[col] = tables.StringCol(df[col].map(len).max())
        else:
            raise ValueError('Unimplemented dtype %s', dt)

    return descr

def _df_to_usable(df):
    if type(df.index) is not pd.RangeIndex:
        df = df.reset_index()
    cols = df.columns
    dtypes = {}
    for c in cols:
        dtypes[c] = df[c].dtype.str
        if 'datetime64' in str(df[c].dtype):
            df[c] = df[c].astype('int64')
    rec = df.to_records(index=False)
    rec_dtypes = []
    for name,dtype in rec.dtype.descr:
        if dtype == '|O':
            rec_dtypes.append('S' + str(df[name].map(len).max()))
        else:
            rec_dtypes.append(dtype)
    rec = np.rec.fromrecords(rec, formats=rec_dtypes,
                             names=rec.dtype.names)

    return (rec, dtypes)
