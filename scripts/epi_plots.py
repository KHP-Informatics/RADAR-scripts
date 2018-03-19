#!/usr/bin/env python3
import os
import glob
import yaml
import pandas as pd
from radar.wrappers import Project
from radar.visualise import interactive
from radar.util import parsers

proj = Project('Data/Epilepsy.h5', subprojects=['KCL', 'UKLFR'])
xcol = 'value.time'
YAML_DIR = 'RADAR-Schemas/specifications/passive'
OUTPUT_DIR = '/path/to/output/plots'
REDCAP_CSV = '/path/to/redcap.csv'
# 5 minutes either size of event plotted
pad = pd.Timedelta('5m')

# Uses the RADAR specification files for axis labels etc.
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

# This sets the data column of interest, but should be unneccessary in the
# future
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
        'value.red', 'value.green', 'value.ir', 'value.dark'],
    'android_biovotion_vsm1_respiration_rate': [
        'value.respirationRate'],
    'android_biovotion_vsm1_temperature': [
        'value.temperature', 'value.temperatureLocal',
        'value.temperatureBarometer'],
}

# The way events are plotted will change, so this format may change.
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

# Only have KCL redcap at the moment.
all_events = parsers.RedcapEpilepsyCSV(REDCAP_CSV).seizures()

for subj_id, subj in proj.participants.items():
    # This is just to skip one of the subprojects
    if subj_id[:3] == 'UKL':
        continue
    # Get events
    events = all_events[subj_id]
    if len(events) == 0:
        continue

    source_list = subj.available_data()
    for source in source_list:
        if source not in ycolumns:
            continue
        ycols = ycolumns[source].copy()
        cols = ycols.copy()
        cols.append(xcol)
        data = subj.df_from_data(source, cols)
        data = data.set_index(xcol)
        data.sort_index(inplace=True)
        for i, event in events.iterrows():
            event = event[['clinical_start', 'clinical_end', 'eeg_start',
                           'eeg_end']]
            if str(event[2]) == 'NaT' or str(event[3]) == 'NaT':
                continue
            timespan = (event[2]-pad, event[3]+pad)
            if data.loc[timespan[0]:timespan[1]].empty:
                continue
            outfile = os.path.join(OUTPUT_DIR, subj_id,
                                   'event_' + str(i),
                                   source + '.html')
            os.makedirs(os.path.dirname(outfile), exist_ok=True)
            fig = interactive.time_span(data, ycols, timespan)
            interactive.add_events(fig, format_event(event))
            fig.xaxis[0].axis_label = 'Time, seizure event starting {}'.format(str(timespan[0]))
            fig.yaxis[0].axis_label = '{} ({})'.format(*data_specs[source])
            fig.title.text = '{}, {}, Event: {}'.format(subj_id, source,
                                                        str(i))
            interactive.save_fig(fig, filename=outfile)
            # interactive.save_fig(fig, filename=outfile[:-4] + 'png',
            #                      filetype='png')
