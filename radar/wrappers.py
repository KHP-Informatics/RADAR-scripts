#!/usr/bin/env python3
import tables
import pandas as pd
from . import visualise
from .io.hdf5 import ProjectFile, RadarTable

class Project():
    def __init__(self, hdf, mode='r', **kwargs):
        if isinstance(hdf, tables.group.Group):
            self._hdf = hdf
            self._is_subproject = True
        elif isinstance(hdf, tables.link.ExternalLink):
            self._hdf = hdf()
            self._is_subproject = True

        elif isinstance(hdf, ProjectFile):
            self._hdf_file = hdf

            self._hdf = hdf.root
            self._is_subproject = False
        else:
            self._hdf_file = ProjectFile(hdf, mode)
            self._hdf = self._hdf_file.root
            self._is_subproject = False

        participants = kwargs.get('participants')
        if participants is None:
            self.participants = self._gen_participants()
        else:
            self.participants = participants
            self.participants.update(self._gen_participants())

        subprojects = kwargs.get('subprojects')
        if subprojects is None:
            self.subprojects = self._gen_subprojects()
        else:
            self.subprojects = {name: self._hdf._f_get_child(name) for
                                name in subprojects}
            self.subprojects.update(self._gen_subprojects())

        self.name = kwargs['name'] if 'name' in kwargs else \
            self._hdf._v_file.filename + self._hdf._v_pathname

        self.parent = kwargs['parent'] if 'parent' in kwargs else None

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

    def __del__(self):
        if hasattr(self, '_hdf_file'):
            self._hdf_file.close()

    def _gen_participants(self):
        participants = AttrRecDict()
        for name, child in self._hdf._v_children.items():
            if isinstance(child, tables.link.Link):
                child = child()
            if not hasattr(child._v_attrs, 'RADAR_TYPE'):
                continue
            if child._v_attrs.RADAR_TYPE == 'SUBPROJECT':
                participants[name] = AttrRecDict()
            elif child._v_attrs.RADAR_TYPE == 'PARTICIPANT':
                participants[name] = Participant(child)
        return participants

    def _gen_subprojects(self):
        subprojects = AttrRecDict()
        for name, child in self._hdf._v_children.items():
            if isinstance(child, tables.link.Link):
                child = child()
            if not hasattr(child._v_attrs, 'RADAR_TYPE'):
                continue
            if child._v_attrs.RADAR_TYPE == 'SUBPROJECT':
                sp = Project(child, participants=self.participants[name],
                             name=name)
                subprojects[name] = sp
        return subprojects

    def add_participant(self, name, subproject=None):
        if subproject is not None:
            if subproject not in self.subprojects:
                raise ValueError('No such subproject: {}'.format(subproject))
            self.subprojects[subproject].add_participant(name)
            return
        if name in self.participants:
            print('Participant {} already exists in the project'.format(name))
            return
        if name not in self._hdf:
            where = self._hdf._v_pathname
            self._hdf._v_file.create_group(where=where, name=name)
        self.participants[name] = Participant(self._hdf._f_get_child(name),
                                              name=name)

    def map_participants(self, func, *args, **kwargs):
        def ptc_func(ptc, *args, **kwargs):
            return func(ptc, *args, **kwargs)
        return map(ptc_func, list(self.participants))


class Participant():
    """ A class to hold data and methods concerning participants/subjects in a
    RADAR trial. Typically intialised by opening a Project.
    Initialisation parameters
    __________
    hdf: tables.Group
        A pytables group object that contains the data relating to the
        participant.
    name: str (optional)
        The name of the participant. If not given it will take a name from the
        hdf group
    parent: radar.Project
        The parent project of the participant.

    Objects
    _______
    data: ParticipantData (dict subclass)
        A dictionary containing each data table in the hdf for the participant.
        It has ease-of-use methods for using the data.
        See also: radar.wrappers.ParticipantData
    info: NotImplemented - will contain info pertaining to the participant
          (sex, age, etc)
    labels: NotImplemented - will contain event labels / times for the data

    """
    def __init__(self, hdf, **kwargs):
        self._hdf = hdf
        self.name = kwargs['name'] if 'name' in kwargs else self._hdf._v_name
        self.parent = kwargs['parent'] if 'parent' in kwargs else None
        self._gen_data()

    def _gen_data(self):
        """ Generates data object for the participant from the hdf group
        Returns
        ______
        self.data: ParticipantData
            Returns the data object that it just set as self.data. Typically
            not used
        """
        self.data = ParticipantData()
        for node in self._hdf._f_iter_nodes():
            if isinstance(node, tables.link.Link):
                node = node()
            if isinstance(node, tables.table.Table):
                node.__class__ = RadarTable
            self.data[node.name] = node
        return self.data

    def plot_time_span(self, source, timespan, ycols,
                       xcol='value.time', fig=None, events=None):
        df = self.df_from_data(source, ycols.append(xcol))
        df.set_index(xcol)
        fig = visualise.interactive.time_span(
            df, ycols, timespan, fig=fig)
        if events != None:
            visualise.interactive.add_events(fig, events)
        return fig

    def df_from_data(self, source, cols=None):
        table = getattr(self._hdf, source)
        if cols is None:
            cols = table.colnames

        df = pd.DataFrame.from_records(table[:][[x for x in cols]])

        for c in cols:
            dtype = getattr(table.attrs, c)
            if dtype != df[c].dtype:
                df[c] = df[c].astype(dtype)

        return df


class ParticipantData(dict):
    def __repr__(self):
        return 'Participant data tables:\n' + ', '.join(list(self.keys()))

    def available(self):
        print('hi')


class RecursiveDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        if key == '/':
            return self
        key_split = key.split('/')
        key = key_split.pop(0)
        if key == '':
            return KeyError('')
        if key_split:
            return dict.__getitem__(self, key).__getitem__('/'.join(key_split))
        else:
            return dict.__getitem__(self, key)


    def _get_x(self, xattr):
        out = []
        for x, v in zip(getattr(self, xattr)(), self.values()):
            if isinstance(v, RecursiveDict):
                out.extend(v._get_x(xattr))
            else:
                out.append(x)
        return out

    def _get_items(self):
        return self._get_x('items')

    def _get_values(self):
        return self._get_x('values')

    def _get_keys(self):
        return self._get_x('keys')

    def __iter__(self):
        return iter(self._get_values())

    def __len__(self):
        return len(self._get_keys())

class AttrRecDict(RecursiveDict):
    def __getattr__(self, name):
        if name not in [x for x in self._get_keys()]:
            raise AttributeError(
                "No such attribute '{}' in '{}'".format(name, self))
        kv = self._get_items()
        val = [x[1] for x in kv if x[0] == name] or None
        if val is None:
            raise AttributeError(
                "No such attribute '{}' in '{}'".format(name, self))
        elif len(val) > 1:
            raise ValueError(
                'Multiple participants with the same ID: {}'.format(name))
        return val[0]

    def __repr__(self):
        repr_string = ('Recursive attribute dictionary: {}\n'
                       'Total items: {}\n'
                       'Top-level keys: {}\n').format(
                           self.__class__,
                           len(self),
                           ', '.join(list(self.keys())))
        return repr_string

