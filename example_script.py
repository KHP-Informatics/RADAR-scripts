#!/usr/bin/env python3
import Util.read_csvs
import matplotlib
matplotlib.use('Agg')
import Visualisation.actogram
import sys

if len(sys.argv) > 1:
    data_folder = sys.argv[1]
else:
    data_folder = '/path/to/data'

accel_data = Util.read_csvs.read_csv_folder_type(data_folder, data_type='android_acceleration')
accel_data['magnitude'] = accel_data[['value.x', 'value.y',
                                      'value.z']].pow(2).sum(axis=1).pow(1/2)
accel_data['magnitude'] = accel_data['magnitude'] - 1
accel_data['magnitude'] = accel_data['magnitude'].abs()
accel_downsamp = accel_data.resample('T').mean() # resamples to every 1min
fig = Visualisation.actogram.plot(accel_downsamp, datacol='magnitude')
fig.savefig('figout.png')
