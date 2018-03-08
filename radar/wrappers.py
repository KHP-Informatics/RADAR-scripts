#!/usr/bin/env python3
import tables
import pandas as pd
import radar.visualise.interactive
import radar.io.hdf5

class Project():
    def __init__(self, hdf, subprojects=None):
        if isinstance(hdf, radar.io.hdf5.ProjectFile):
            self.hdf_file = hdf
            self.hdf = hdf.root
        elif isinstance(hdf, tables.group.Group):
            self.hdf = hdf
        else:
            self.hdf_file = radar.io.hdf5.ProjectFile(hdf, 'r')
            self.hdf = self.hdf_file.root

        self.subprojects = subprojects
        self._gen_participants()


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
        fig = radar.visualise.interactive.time_span(
            df, ycols, timespan, fig=fig)
        if events != None:
            radar.visualise.interactive.add_events(fig, events)
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
