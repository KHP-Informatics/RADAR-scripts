#!/usr/bin/env python3
import glob
import yaml
from ..defaults import _SPECIFICATION_DIR

class ProjectSpecs(dict):
    """
    A class to hold all YML specifications relating to a RADAR project
    """
    def __init__(self, spec_dir: str = _SPECIFICATION_DIR):
        """
        A path (str) to a RADAR specification directory should be given to
        initialise the class. It will use the package default specifications if
        no path is given.
        """
        print(spec_dir)


class DeviceSpec(dict):
    """
    A class to store RADAR YML specifications
    """
    def __init__(self, specification_file: str):
        with open(specification_file) as f:
            self._yml = yaml.load(f.read())
        self['Device'] = self._yml['vendor'] + ' ' + self._yml['model']


class ModalitySpec(dict):
    """
    A class to store the modalities of a RADAR specification.
    """

    def __init__(self, modal):
        super(ModalitySpec, self).__init__(modal)


class FieldSpec(dict):
    """
    A class to store fields of modalities in RADAR specifications.
    """
    def __init__(self, field):
        super(FieldSpec, self).__init__(field)


