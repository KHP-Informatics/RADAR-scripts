#!/usr/bin/env python3
import Util.load_csvs
import Visualisation.actogram
import sys

if sys.argv[1]:
    data_folder = sys.argv[1]
else:
    data_folder = '/path/of/data'

accel_data = Util.load_csvs.read_csv_folder_type(data_folder, data_type='acceleration')
accel_data['magnitude'] = accel_data[['value.x', 'value.y',
                                      'value.z']].pow(2).sum(axis=1)
accel_data['magnitude'] = accel_data['magnitude'] - 1
accel_data['magnitude'] = accel_data['magnitude'].abs()
accel_downsamp = accel_data.resample('T').mean() # resamples to every 1min
# actogram.plot currently splits hourly, will change to daily
fig = Visualisation.actogram.plot(accel_downsamp, datacol='magnitude')
fig.savefig('figout.png')
