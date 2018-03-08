#!/usr/bin/env python3
import os
import glob
import yaml
from radar.util.avro import RadarSchema
from radar.wrappers import Project
from radar.visualise import interactive
from radar.util import parsers

proj = Project('Data/Epilepsy.h5')
xcol = 'value.time'
SCHEMA_DIR = '/Users/callum/RADAR/RADAR-Schemas/commons/passive'
YAML_DIR = '/Users/callum/RADAR/RADAR-Schemas/specifications/passive'
UKLFR_DIR = '/Users/callum/RADAR/Data/Epilepsy/UKLFR'
OUTPUT_DIR = '/Users/callum/RADAR/plots'
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

# hmm
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

def format_event(event):
    ev_form = []
    y = 0
    if event[0]:
        ev_form.append(['Clinical Start', (event[0], y)])
        y += 10
    if event[1]:
        ev_form.append(['Clinical End', (event[1], y)])
        y += 10
    if event[2]:
        ev_form.append(['EEG Start', (event[2], y)])
        y += 10
    if event[3]:
        ev_form.append(['EEG End', (event[3], y)])
    return ev_form

for subj_id, subj in proj.participants.items():
    if subj_id[:3] == 'KCL':
        continue

    ext_csv = glob.glob(UKLFR_DIR+'/'+subj_id+'/*_ext.csv')[0]
    with open(ext_csv, 'r') as f:
        events, labels = parsers.uklfr_subject_ext_csv(f)
    if len(events) == 0:
        continue

    source_list = subj.available_data()
    for i, event in enumerate(events):
        for source in source_list:
            ycols = ycolumns[source]
            timespan = (event[2]-300, event[3]+300)
            outfile = os.path.join(OUTPUT_DIR, subj_id,
                                   'event_' + str(i),
                                   source + '.html')
            try:
                fig = subj.plot_time_span(source, timespan, ycols,
                                          events=format_event(event))
                interactive.save_fig(fig, filename=outfile)
            except:
                print('Skipping')
