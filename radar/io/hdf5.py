#!/usr/bin/env python3
import os
import tables
import numpy as np
import pandas as pd
from ..common import AVRO_HDF_TYPE, NP_HDF_CONVERSION, obj_col_names
from ..common import progress_bar
from ..defaults import _FILTER
from radar import Project

def open_project_file(filename, mode='r', title='', root_uep='/',
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
                    'The file "{}" is already opened. Can\'t ',
                    'reopen in write mode', filename)
    return ProjectFile(filename, mode, title, root_uep, filters, **kwargs)


def project_from_csvs(project_file, folder_path, subprojects=None,
                      schemas=None, **kwargs):
    """ Creates a RADAR project HDF5 file containing data from CSV files.
    The filesystem folders should be organised as in the RADAR-CNS FTP, with a
    project folder containing participant folders, which each contain data
    source/modality folders with CSV files inside.
    Subprojects may be specified if the top level directory does not
    contain participants as child folders

    Parameters
    __________
    project_file (required): str or radar.io.hdf5.ProjectFile
        The HDF5 file to copy data in to.
    folder_path (required): str
        Path to the filesystem project directory
    subprojects (optional): list or None
        A list of subprojects to look for participants in. Paths relative to
        folder_path.
    specifications (optional): dict / radar.util.avro.ProjectSchemas
        A dictionary containing schema names and the associated RadarSchema
        object. Default uses default package specifications.
    specs_only (optional): Bool
        Whether to only load data from modalities with a known specification.
        If False, the datatype will be inferred.
        Default is True
    participant_subfolders (optional): Bool
        Whether to recreate the heirarchy of folders underneath each
        participant. Default is False.
    custom_subfolder (optional): str
        An optional folder under which to put all participant data modalities.
        Default is '' (No subfolder)

    Returns
    _______
    Project: radar.wrappers.Project
        A RADAR project wrapper around the new HDF5 file.
    """
    def create_participants(subproject_relpath):
        sp_dir = os.path.join(folder_path, subproject_relpath)
        for ptc in participant_dirs(sp_dir):
            participant_from_csvs(project_file=project_file,
                                  where=subproject_relpath,
                                  name=ptc,
                                  folder_path=os.path.join(sp_dir, ptc),
                                  **kwargs)


    def participant_dirs(path):
        return [f for f in os.listdir(path) if
                os.path.isdir(os.path.join(path, f))]

    if isinstance(project_file, str):
        project_file = open_project_file(project_file, 'a')
    if subprojects is None:
        subprojects = []
        create_participants('')

    for sp in subprojects:
        print(sp)
        where, name = os.path.split(sp)
        sp_hdf = project_file.create_group(where, name)
        setattr(sp_hdf._v_attrs, 'RADAR_TYPE', 'SUBPROJECT')
        create_participants(sp)

    return Project(project_file)


def participant_from_csvs(project_file, where, name, folder_path,
                          schemas_only=True, schemas_dir=_SCHEMA_DIR,
                          participant_subfolders=False, custom_subfolder=''):
    ptc_hdf = project_file.create_group(where, name)
    folders = set([os.path.split(f)[0] for f in
                   glob.glob(folder_path+'/**/*.csv', recursive=True)])



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
    raise NotImplementedError('TODO: make dict')
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
                 filters=_FILTER, subprojects=None, **kwargs):
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
                obj = obj.to_records(index=False)
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


    def save_dataframe(self, df, where, name, source_type='DATA', **kwargs):
        """Add a pandas dataframe to an entrypoint in the hdf5 file
        """
        df, attrib_types = _df_to_usable(df)
        table = self.create_radar_table(where, name, obj=df, **kwargs)
        for k, v in attrib_types.items():
            setattr(table.attrs, k, v)
        setattr(table.attrs, 'NAME', name)
        setattr(table.attrs, 'RADAR_TYPE', source_type)
        return table

class ParticipantGroup(tables.Group):
    """ A Pytables group object for use with RADAR participants.
    Currently a pure Pytables Group object, here in case there is use in the
    future.
    """
    pass

class RadarTable(tables.Group):
    """ A Table object for RADAR data
    Parameters
    _________
    See also
    ________
    tables.Table : For more information on the PyTables Table object
    """
    def __init__(self, parentnode, name,
                 descr=None, obj=None,
                 filters=_FILTER, **kwargs):
        super(RadarTable, self).__init__(parentnode, name, filters=_FILTER, **kwargs)
        if descr:
            if obj:
                if len(descr) > 1:
                    pass
                else:
                    self.insert_array(list(descr)[0])

    def _item_parse(self, item):
        cols = None
        index = None
        if isinstance(item, tuple):
            """redo this"""
            if len(item) > 2:
                raise IndexError(('Only subscriptable with a row index '
                                  '(number or slice, numpy indexing allowed), '
                                  'and/or column name(s)'))
            cols = [x for x in item if
                    (isinstance(x, list) and isinstance(x[0], str))][0]
            cols = [x for x in item if isinstance(x, str)]
            index = [x for x in item if isinstance(x, slice) or
                    (isinstance(x, list) and isinstance(x[0], int))][0]
        elif isinstance(item, slice):
            index = item
        elif isinstance(item, str):
            cols = [item]
        elif isinstance(item, list):
            if isinstance(item[0], str):
                cols = item
            elif isinstance(item[0], int):
                index = item
            else:
                raise TypeError(('A given list should only contain column '
                                 'names or row indexes'))
        else:
            raise IndexError(('Only subscriptable with a row index '
                              '(number or slice, numpy indexing allowed), '
                              'and/or column name(s)'))
        if cols is None:
            cols = [c._v_name for c in self._f_iter_nodes()]
        if index is None:
            index = slice(None)

        return (cols, index)

    def _col_dtypes(self, column_names=None):
        if column_names is None:
            column_names = [c._v_name for c in self._f_iter_nodes()]
        for col in column_names:
            if hasattr(col._v_attrs, np_dtype):
                dtypes[col._v_name] = col._v_attrs.np_dtype


    def __getitem__(self, item):
        """Returns the columns and/or indexes specified from the RADAR table.
        Parameters
        __________
        item: str, slice, list
            May be a column name, list of column names, a slice, or a
            combination of a slice and column name(s).
            e.g.
            RadarTable[0:100] for index 0 to 100 of all columns.
            RadarTable['c1'] for the entirety of column c1.
            RadarTable[['c1', 'c2']] for the entireties of columns 'c1' and
                'c2'
            RadarTable['c1', 5:25] for index 5 to 25 of column 'c1'
            RadarTable[['c1', 'c3'], -25:] for the final 25 values of columns
                'c1' and 'c3'.

        Returns
        _______
        table : pandas.DataFrame
            Returns a pandas DataFrame made from the given columns and indexes

        """
        cols, index = self._item_parse(item)
        dtypes = _col_dtypes(cols)
        return pd.DataFrame({c: self._f_get_child(c)[index]
                             for c in cols}).astype(dtypes)

    def __setitem__(self, item, df):
        """Sets the column(s) at the given index to the values in the given
        dataframe. The dataframe must have the same columns as the table, or
        a subset of table columns must be given.
        Parameters
        __________
        item: slice, list
            Must be a slice or a slice and column name(s)
            e.g.
            RadarTable[0:100] = df
            RadarTable[0:100, 'c1'] = df
            RadarTable[0:100, ['c1', 'c2', 'c3']] = df
        df: pandas.DataFrame
            A dataframe with the same columns as the table/given as the item.
            Alternatively, if only one column is selected, may be a numpy array
            or python list.

        """
        cols, index = self._item_parse(item)
        if len(cols) == 1 and (isinstance(df, np.ndarray) or
                               isinstance(df, list)):
            self._f_get_child(cols[0])[index] = np.ndarray
            return

        if len(df.columns) != len(cols):
            raise ValueError(('DataFrame must have the same number of '
                              'columns as the table, or the table columns '
                              'must be given'))
        if not all([x in cols for x in df]):
            raise ValueError(('The dataframe must have the same column names '
                              'as the table'))

        for col in cols:
            self._f_get_child(col)[index] = df[col].values

    def insert_dataframe(self, df, descr=None, overwrite=False, attrs=None):
        for col in obj_col_names(df):
            self.insert_array(df[col], name=col, descr=descr[col], attrs=attrs)

    def append_dataframe(self, df, create_columns=True):
        for col in obj_col_names(df):
            self.append_array(df[col], name=col,
                              create_column=create_columns)

    def insert_array(self, arr, name, overwrite=False, attrs=None):
        if name in self._v_children:
            if overwrite:
                self._hdf._f_getChild(name).remove()
            else:
                raise ValueError(('There is already a column "{}" in table'
                                  '{}'.format(name, self._v_name)))

        if isinstance(arr, pd.Series):
            arr = arr.values

        dt = arr.dtype.str
        if attrs is not None:
            attrs[name] = dt
        else:
            attrs = {name: dt}
        if dt in NP_HDF5_CONVERSION:
            arr = NP_HDF5_CONVERSION[dt](arr)

        self._v_file.create_earray(self, name=name, title=name, obj=arr)
        for k, v in attrs.items():
            setattr(self._f_get_child(name)._v_attrs, k, v)

    def append_array(self, arr, name, create_column=True):
        if name not in self._v_children:
            if create_column:
                self.insert_array(arr, name)
            else:
                raise ValueError(('There is no such column {} '
                                  'and create_column is set to '
                                  'False'.format(name)))
        else:
            self._f_getChild(name).append(arr)


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
