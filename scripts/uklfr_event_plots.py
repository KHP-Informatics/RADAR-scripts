#!/usr/bin/env python3
import glob
import yaml
import os
from radar.util.avro import RadarSchema
from radar.util.parsers import uklfr_subject_ext_csv
from radar.visualise import interactive

SCHEMA_DIR = '/Users/callum/RADAR/RADAR-Schemas/commons/passive'
YAML_DIR = '/Users/callum/RADAR/RADAR-Schemas/specifications/passive'
UKLFR_DIR = '/Users/callum/RADAR/Data/Epilepsy/UKLFR'
OUTPUT_DIR = '/Users/callum/RADAR/plots'

# this needs to change
ycolumns = {
    'android_empatica_e4_acceleration': ['value.x', 'value.y', 'value.z'],
    'android_empatica_e4_blood_volume_pulse': ['value.bloodVolumePulse'],
    'android_empatica_e4_electrodermal_activity': [
        'value.electroDermalActivity'],
    'android_empatica_e4_inter_beat_interval': [
        'value.interBeatInterval'],
    'android_empatica_e4_temperature': ['value.temperature'],
    'android_biovotion_vsm1_acceleration' : [
        'value.x', 'value.y', 'value.z'],
    'android_biovotion_vsm1_blood_pulse_wave': [
        'value.bloodPulseWave'],
    'android_biovotion_vsm1_energy': [
        'value.energyExpenditure'],
    'android_biovotion_vsm1_galvanic_skin_response': [
        'value.galvanicSkinResponseAmplitude'],
    'android_biovotion_vsm1_heartRateVariability': [
        'value.heartRateVariability'],
    'android_biovotion_vsm1_heart_rate': [
        'value.heartRate'],
    'android_biovotion_vsm1_led_current': [
        'value.red', 'value.green', 'value.ir', 'value.offset'],
    'android_biovotion_vsm1_oxygen_saturation': [
        'value.spO2'],
    'android_biovotion_vsm1_ppg_raw': [
        'value.red', 'value.green', 'value.ir', 'value,dark'],
    'android_biovotion_vsm1_respiration_rate': [
        'value.respiration_rate'],
    'android_biovotion_vsm1_temperature': [
        'value.temperature', 'value.temperatureLocal',
        'value.temperatureBarometer'],
}

def make_event_dict(event):
    ev_dict = {}
    y = 0
    if event[0]:
        ev_dict['Clinical Start'] = (event[0], y)
        y += 10
    if event[1]:
        ev_dict['Clinical End'] = (event[1], y)
        y += 10
    if event[2]:
        ev_dict['EEG Start'] = (event[2], y)
        y += 10
    if event[3]:
        ev_dict['EEG End'] = (event[3], y)
    return ev_dict
schemas = {}
for schema_path in glob.glob(SCHEMA_DIR+'/**/*.avsc'):
    with open(schema_path, 'r') as f:
        name = 'android_' + schema_path.split('/')[-1][:-5]
        schemas[name] = RadarSchema(value_json=f.read())

data_specs = {}
for yml in glob.glob(YAML_DIR + '/*.yml'):
    with open(yml, 'r') as f:
        for d in yaml.load(f)['data']:
            try:
                dtopic = d['topic']
            except:
                continue
            try:
                dtype = d['type'].capitalize().replace('_', ' ')
            except:
                dtype = '?'
            try:
                dunit = d['unit'].lower().replace('_', ' ').replace(' per ', '/')
            except KeyError:
                dunit = ''
            data_specs[dtopic] = (dtype, dunit)

for folder in glob.glob(UKLFR_DIR+'/UKLFR*'):
    userId = folder.split('/')[-1]
    print(userId)
    ext_csv = glob.glob(folder+'/*_ext.csv')[0]
    with open(ext_csv, 'r') as f:
        events, labels = uklfr_subject_ext_csv(f)
    if len(events) == 0:
        continue

    data_modalities = {}
    for data_folder in [x for x in glob.glob(folder + '/*')]:
        data_name = data_folder.split('/')[-1]
        if data_name in ycolumns and data_name in schemas:
            print('Loading {}....'.format(data_name))
            data_modalities[data_name] = \
                schemas[data_name].load_csv_folder(data_folder)
            print(data_modalities[data_name])

    for i, event in enumerate(events):
        print(i)
        print(event)
        for data_name, data in data_modalities.items():
            try:
                if event[2] < data.index.min() or event[3] > data.index.max():
                    continue
            except TypeError:
                continue
            data = data.set_index('value.timeReceived')
            print('{} Event: {}, Data: {}'.format(userId, i, data_name))
            ycols = ycolumns[data_name]
            timespan = (event[2]-180, event[3]+180)
            event_dict = make_event_dict(event)
            fig = interactive.time_span(data, ycols, timespan)
            interactive.add_events(fig, event_dict)
            fig.xaxis[0].axis_label = 'Time, seizure event starting' + \
                    ': {} CET'.format(str(timespan[0]+7200))
            fig.yaxis[0].axis_label = '{} ({})'.format(*data_specs[data_name])
            fig.title.text = '{}, {}, Event: {}'.format(userId, data_name,
                                                        str(i))
            outfile = os.path.join(OUTPUT_DIR, userId,
                                   'event_' + str(i),
                                   data_name + '.html')
            os.makedirs(os.path.dirname(outfile), exist_ok=True)
            interactive.save_fig(fig, filename=outfile)
            interactive.save_fig(fig, outfile[:-5]+'.png', 'png')
