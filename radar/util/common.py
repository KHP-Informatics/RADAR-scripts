import numpy as np
import h5py

PRIMITIVE_TYPES = (
    'null',
    'boolean',
    'int',
    'long',
    'float',
    'double',
    'bytes',
    'string',
)

COMPLEX_TYPES = (
    'record',
    'enum',
    'array',
    'map',
    'union'
    'fixed',
)

TYPE_ATTRIBUTES = {
    'record': (
        'name',
       'namespace',
       'doc',
       'aliases',
       'fields',
       'order',
    ),
    'fields': (
        'name',
        'doc',
        'type',
        'default',
        'order',
        'aliases',
    ),
    'enum': (
        'name',
        'namespace',
        'aliases',
        'doc',
        'symbols',
    ),
    'array': (
        'items',
    ),
    'map': (
        'values',
    ),
    'union': (),
    'fixed': (
        'name',
        'namespace',
        'aliases',
        'size',
    ),
}

AVRO_NUMPY_TYPES = {
    'null': None,
    'boolean': np.bool_,
    'int': np.int32,
    'long': np.int64,
    'float': np.float32,
    'double': np.float64,
    'bytes': np.bytes_,
    'string': np.object,
    'enum': np.object,
}

PD_HDF_TYPES = {
    'object': h5py.special_dtype(vlen=str),
    'int64': 'i8',
    'datetime64[ns]': 'i8',
    'float32': 'f',
}

AVRO_HDF_TYPE = {
    'null': 1,
    'boolean': 1,
    'int': 1,
    'long': 1,
    'float': 1,
    'double': 1,
    'bytes': 1,
    'string': 1,
    'enum': 1,
}
