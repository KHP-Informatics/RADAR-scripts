#!/usr/bin/env python3
import tables
import pandas as pd
from . import visualise
from . import io

class Project():
    def __init__(self, hdf, subprojects=None, **kwargs):
        if isinstance(hdf, io.hdf5.ProjectFile):
            self.hdf = hdf.root
        elif isinstance(hdf, tables.group.Group):
            self.hdf = hdf
        else:
            self.hdf_file = io.hdf5.ProjectFile(hdf, 'r')
            self.hdf = self.hdf_file.root

        if subprojects is not None:
            self.subprojects = {sp: Project(getattr(self.hdf, sp), name=sp)
                                for sp in subprojects}
        else:
            self.subprojects = None

        self._gen_participants()
        self.name = kwargs['name'] if 'name' in kwargs else ''

    def __str__(self):
        return self.name

    def __repr__(self):
        info_string = '''member of {class}
        Project name: {name}
        Subprojects: {subprojs}
        No. participants: {num_partic}
        '''
        format_kwargs = {'class': type(self),
                         'name': self.name,
                         'subprojs': str(self.subprojects),
                         'num_partic': len(self.participants),
                        }
        return info_string.format(**format_kwargs)

    def __del__(self):
        if hasattr(self, 'hdf_file'):
            self.hdf_file.close()

    def _resolve_subprojects(self, subprojects_list):

        return -1


    def _gen_participants(self):
        self.participants = {}
        if self.subprojects:
            for sp in self.subprojects:
                sp_hdf = getattr(self.hdf, sp)
                for partic in getattr(sp_hdf, '_v_children'):
                    self.participants[partic] = \
                        Participant(getattr(sp_hdf, partic), name=partic)
        else:
            for partic in getattr(self.hdf, '_v_children'):
                self.participants[partic] = \
                        Participant(getattr(self.hdf, partic), name=partic)
        return list(self.participants)

    def add_participant(self, name, subproject=None):
        if subproject is not None:
            if subproject not in self.subprojects:
                raise ValueError('No such subproject: {}'.format(subproject))
            self.subprojects[subproject].add_participant(name)
            self._gen_participants()
            return
        if name in self.participants:
            print('Participant {} already exists in the project'.format(name))
            return
        if name not in self.hdf:
            where = self.hdf._v_pathname
            self.hdf._v_file.create_group(where=where, name=name)
        self.participants[name] = Participant(self.hdf, name=name)


class Participant():
    def __init__(self, hdf, name):
        self.hdf = hdf
        self.name = name

    def available_data(self):
        return [source.name for source in self.hdf._f_iter_nodes()]

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
        table = getattr(self.hdf, source)
        if cols is None:
            cols = table.colnames

        df = pd.DataFrame.from_records(table[:][[x for x in cols]])

        for c in cols:
            dtype = getattr(table.attrs, c)
            if dtype != df[c].dtype:
                df[c] = df[c].astype(dtype)

        return df
