#!/usr/bin/env python3
import os
import glob
from . import visualise
from .common import AttrRecDict, progress_bar
from .io.hdf5 import ProjectFile, RadarDataGroup, open_project_file
from .io.csv import read_folder
from .util.specifications import ProjectSpecs
from .util.avro import ProjectSchemas

class Project():

    def from_h5(self, h5_path, *args, **kwargs):
        pass

    def from_csvs(self, folder_path, *args, **kwargs):
        pass

    def load_h5(self, h5_path, *args, **kwargs):
        pass

    def load_csvs(self, folder_path, *args, **kwargs):
        pass

    def to_h5(self, h5_path, *args, **kwargs):
        pass

    def to_csvs(self, folder_path, *args, **kwargs):
        pass

    def _get_subprojects(self, subproject_data_dict):
        for sp_name, sp_data in subproject_data_dict.items():
            self.add_subproject(sp_name, data=sp_data)

    def _get_participants(self, participant_data_dict):
        for ptc_name, ptc_data in participant_data_dict.items():
            if not isinstance(ptc_data, AttrRecDict):
                if not isinstance(ptc_data, dict):
                    ptc_data = ptc_data.get_data_dict()
                self.add_participant(ptc_name, data=ptc_data)

    def add_participant(self, name, where='.', data=None, info=None):
        proj = self if where == '.' else self.subprojects[where]
        proj.participants[name] = Participant(data=data, name=name, info=info)
        return proj.participants[name]

    def add_subproject(self, name, where='.', data=None):
        proj = self if where == '.' else self.subprojects[where]
        proj.participants[name] = AttrRecDict()
        proj.subprojects[name] = Project(data, name=name, parent=self)
        return proj.subprojects[name]

    def __init__(self, proj_data=None, **kwargs):
        self.name = kwargs['name'] if 'name' in kwargs else proj_data.name
        self.parent = kwargs['parent'] if 'parent' in kwargs else None
        self._data = [proj_data] if proj_data is not None else []
        self.subprojects = AttrRecDict()
        self.participants = self.parent.participants[self.name] if self.parent \
                        else AttrRecDict()
        if self._data :
            self._get_subprojects(proj_data.subprojects)
            self._get_participants(proj_data.participants)

    def __str__(self):
        return 'RADAR {}: {}, {} participants'.format(
            'Project' if hasattr(self, '_hdf_file') else 'Subproject',
            self.name,
            len(self.participants))

    def __repr__(self):
        info_string = '''member of {class}
        Name: {name}
        Subprojects: {subprojs}
        No. participants: {num_partic}
        '''
        format_kwargs = {'class': type(self),
                         'name': self.name,
                         'subprojs': ', '.join(self.subprojects.keys()) or 'None',
                         'num_partic': len(self.participants),
                        }
        return info_string.format(**format_kwargs)

    def map_participants(self, func, *args, **kwargs):
        def ptc_func(ptc, *args, **kwargs):
            return func(ptc, *args, **kwargs)
        return map(ptc_func, list(self.participants))


class Participant():
    """ A class to hold data and methods concerning participants/subjects in a
    RADAR trial. Typically intialised by opening a Project.
    """
    def __init__(self, data=None, info=None, **kwargs):
        self.data = data if data is not None else {}
        self.info = info if info is not None else {}
        self.name = kwargs['name'] if 'name' in kwargs else data.name
        self.parent = kwargs['parent'] if 'parent' in kwargs else None

    def __repr__(self):
        return "Participant {}. of type {}".format(self.name, type(self))

    def plot_time_span(self, source, timespan, ycols,
                       xcol='value.time', fig=None, events=None):
        df = self.df_from_data(source, ycols.append(xcol))
        df.set_index(xcol)
        fig = visualise.interactive.time_span(
            df, ycols, timespan, fig=fig)
        if events != None:
            visualise.interactive.add_events(fig, events)
        return fig
