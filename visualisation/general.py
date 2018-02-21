#!/usr/bin/env python3
import matplotlib.pyplot as plt

def group_plot(dataframe, ycols, groupby, xcol=None, **plotkwargs):
    groups = dataframe.groupby(groupby)[ycols]
    f = plt.figure()
    z = 1
    for label, group in groups:
        ax = plt.subplot(len(groups), 1, z)
        group.plot(y=ycols, x=xcol, ax=ax, **plotkwargs)
        z = z + 1
    plt.subplots_adjust(hspace=0)
    return f

