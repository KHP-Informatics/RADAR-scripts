#!/usr/bin/env python3
import matplotlib.pyplot as plt

def plot(dataframe):
    z = 1
    groups = dataframe.groupby(dataframe.index.hour)
    for labels, group in groups:
        plt.subplot(len(groups), 1, z)
        group.plot(y='value.x')
        plt.xticks(visible=False)
        plt.yticks(visible=False)
        plt.subplots_adjust(hspace=0)
        plt.ylim(-5, 5)
        z = z + 1
    plt.show()
