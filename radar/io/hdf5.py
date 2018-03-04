#!/usr/bin/env python3
import tables
from util.common import AVRO_HDF_TYPE
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
        tables.File().__init__(filename, mode, title, root_uep, filters,
                               **kwargs)
        self.subprojects = subprojects

    def create_radar_table(self, where, name, description=None, title='',
                     filters=_FILTER, expectedrows=1000000,
                     chunkshape=None, byteorder=None,
                     create_parents=True, obj=None):
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
        parentnode = self._get_or_create_path(where, create_parents)
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

    def create_table_schema(self, where, name, schema, create_parents=True,
                            **kwargs):
        """ Create a new table based on a given schema TODO
        """
        description = schemafunc(schema)
        self.create_radar_table(where, name, description=description, **kwargs)


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
        tables.Table().__init__(parentnode, name, filters=_FILTER, **kwargs)


