#!/usr/bin/env python3
import os
import glob
import tables
import pandas as pd
from . import visualise
from .common import AttrRecDict, progress_bar
from .io.hdf5 import ProjectFile, RadarTable, open_project_file
from .io.csv import read_folder
from .util.specifications import ProjectSpecs
from .util.avro import ProjectSchemas

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

    def __repr__(self):
        return "Participant {}. of type {}".format(self.name type(self))

    def _gen_data(self):
        """ Generates data object for the participant from the hdf group
        Returns
        ______
        self.data: ParticipantData
            Returns the data object that it just set as self.data. Typically
            not used
        ____
        Notes: This should probably be refactored so that HDF5 specific
        functions are put into a hdf5 specific class under .io
        """
        self.data = ParticipantData()
        for node in self._hdf._f_iter_nodes():
            if isinstance(node, tables.link.Link):
                node = node()
            if isinstance(node, tables.group.Group):
                node.__class__ = RadarTable
            self.data[node._v_name] = node
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


class ParticipantData(dict):
    def __repr__(self):
        return 'Participant data tables:\n' + ', '.join(list(self.keys()))

    def available(self):
        print(self.__repr__())


def project_from_csvs(folder_path: str,
                      project_file: str = None,
                      subprojects: list = None,
                      schemas: ProjectSchemas = None,
                      specifications: ProjectSpecs = None,
                      use_schemas: bool = False,
                      use_specs: bool = False,
                      load_only_schemas: bool = False):
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
    Returns
    _______
    Project: radar.wrappers.Project
        A RADAR project wrapper around the new HDF5 file.
    """
    def create_participants(subproject_relpath):
        sp_dir = os.path.join(folder_path, subproject_relpath)
        for ptc in participant_dirs(sp_dir):
            if ptc not in project_file.get_node('/' + subproject_relpath):
                ptc_hdf = project_file.create_group('/' + subproject_relpath, ptc)
                setattr(ptc_hdf._v_attrs, 'RADAR_TYPE', 'PARTICIPANT')
            participant_from_csvs(project_file=project_file,
                                  where=subproject_relpath,
                                  name=ptc,
                                  folder_path=os.path.join(sp_dir, ptc),
                                  schemas=schemas,
                                  specifications=specifications,
                                  use_schemas=use_schemas,
                                  use_specs=use_specs,
                                  load_only_schemas=load_only_schemas)


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
        sp_hdf = project_file.create_group('/' + where, name)
        setattr(sp_hdf._v_attrs, 'RADAR_TYPE', 'SUBPROJECT')
        create_participants(sp)

    return Project(project_file)


def participant_from_csvs(project_file,
                           where,
                           name,
                           folder_path,
                           schemas: ProjectSchemas,
                           specifications: ProjectSpecs,
                           use_schemas: bool = True,
                           use_specs: bool = False,
                           load_only_schemas: bool = False,
                           participant_subfolders=False,
                           custom_subfolder=''):
    folders = set([os.path.split(f)[0] for f in
                   glob.glob(folder_path+'/**/*.csv', recursive=True)])
    print(folder_path)
    for modal_path in folders:
        modal = os.path.split(modal_path)[-1]
        print(modal)
        if load_only_schemas:
            if modal not in schemas:
                print('{} not in schemas. Skipping...'.format(modal))
                continue
        df = read_folder(path=modal_path,
                         schema=schemas[modal] if use_schemas else None,
                         specification=specifications[modal] \
                                 if use_specs else None)
        print(where)
        ptab = project_file.save_dataframe(df,
                                           where='/' + where + '/' + name,
                                           name=modal,
                                           source_type='PASSIVE')
