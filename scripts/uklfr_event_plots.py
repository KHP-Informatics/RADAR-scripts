#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import util.avro, util.parsers, visualise.general
import glob
SCHEMA_DIR = '/Users/callum/RADAR/RADAR-Schemas/commons/passive/empatica/'
UKLFR_DIR = '/Users/callum/RADAR/Data/Epilepsy/UKLFR/'

with open(SCHEMA_DIR+'empatica_e4_acceleration.avsc', 'r') as f:
    accel_schema = util.avro.RadarSchema(value_json=f.read())

with open(SCHEMA_DIR+'empatica_e4_blood_volume_pulse.avsc', 'r') as f:
    bvp_schema = util.avro.RadarSchema(value_json=f.read())

with open(SCHEMA_DIR+'empatica_e4_electrodermal_activity.avsc', 'r') as f:
    eda_schema = util.avro.RadarSchema(value_json=f.read())


for folder in glob.glob(UKLFR_DIR+'UKLFR*'):
    ext_csv = glob.glob(folder+'/*_ext.csv')[0]
    with open(ext_csv, 'r') as f:
        events, labels = util.parsers.uklfr_subject_ext_csv(f)
    if len(events) == 0:
        continue

    accel_data = accel_schema.load_csv_folder(folder+'/android_empatica_e4_acceleration')
    bvp_data = bvp_schema.load_csv_folder(folder+'/android_empatica_e4_blood_volume_pulse')
    eda_data = eda_schema.load_csv_folder(folder+'/android_empatica_e4_electrodermal_activity')

    for i, event in enumerate(events):
        try:
            if event[2] < accel_data.index.min() or event[3] > accel_data.index.max():
                continue
        except TypeError:
            continue
        f = plt.figure()
        visualise.general.time_view([accel_data, bvp_data, eda_data],
                                    (event[2]-180, event[3]+180),
                                    [['value.x','value.y','value.z'],
                                     ['value.bloodVolumePulse'],
                                     ['value.electroDermalActivity']],
                                    fig=f)
        f.savefig(folder+'/'+str(i)+'.png')
