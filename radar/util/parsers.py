#!/usr/bin/env python3
import numpy as np

NAT = np.datetime64('NaT')

def uklfr_subject_ext_csv(csv):
    """ A parser to extract seizure event times from the UKLFR _ext.csv files
    Parameters
    __________
    csv: StringIO
        A file handle to the CSV file.

    Returns
    _______
    events: np.array
        A 4 column numpy datetime64 array containing merged labels. Each row
        corresponds to one seizure event.
        The columns are: 
            - clinician start time
            - clinician end time
            - EEG start time
            - EEG end time
    labels: dict
        A dictionary with keys:
        ['clin_start', 'clin_end', 'eeg_start', 'eeg_end']
        Each entry is a 1D numpy datetime64 array with the time of the label
        entry.
    """
    def determine_events(labels):
        def nearest_end(start, ends, cutoff=600):
            cutoff = np.timedelta64(cutoff, 's')
            try: 
                nearest_end = ends[(ends > start).argmax()]
            except ValueError:
                return NAT
            if not nearest_end:
                return NAT
            elif nearest_end - start < cutoff:
                return nearest_end
            else:
                return NAT
        
        def merge_events(clin_events, eeg_events, cutoff=120):
            events = []
            used_eeg = []
            cutoff = np.timedelta64(cutoff, 's')
            for i, c_ev in enumerate(clin_events):
                events.append([c_ev[0], c_ev[1], NAT, NAT])
                start_diffs = abs(eeg_events[:, 0] - c_ev[0])
                if any(start_diffs < cutoff):
                    eeg_idx = start_diffs.argmin()
                    used_eeg.append(eeg_idx)
                    events[i][2] = eeg_events[eeg_idx, 0]
                    events[i][3] = eeg_events[eeg_idx, 1]
            
            for i, e_ev in enumerate(eeg_events):
                if i in used_eeg:
                    continue
                events.append([NAT, NAT, e_ev[0], e_ev[1]])

            return np.array(events, dtype='datetime64')
                    

        clin_events = np.zeros((len(labels['clin_start']), 2),
                                dtype='datetime64[s]')
        for i in range(len(labels['clin_start'])):
            clin_events[i, 0] = labels['clin_start'][i]
            clin_events[i, 1] = nearest_end(start=labels['clin_start'][i],
                                            ends=labels['clin_end'])

        eeg_events = np.zeros((len(labels['eeg_start']), 2),
                              dtype='datetime64[s]')
        for i in range(len(labels['eeg_start'])):
            eeg_events[i, 0] = labels['eeg_start'][i]
            eeg_events[i, 1] = nearest_end(start=labels['eeg_start'][i],
                                           ends=labels['eeg_end'])

        return merge_events(clin_events, eeg_events)

    contents = [line.rstrip().split('|') for line in csv.readlines()]
    labels = {
        'clin_start': [],
        'clin_end': [],
        'eeg_start': [],
        'eeg_end': [],
    }
    for line in contents[1:]:
        time = int(line[0])
        if 'klin.AB' in line[5]:
            labels['clin_start'].append(time)
        elif 'klin.AE' in line[5]:
            labels['clin_end'].append(time)
        elif 'EEG-AB' in line[5]:
            labels['eeg_start'].append(time)
        elif 'EEG-AE' in line[5]:
            labels['eeg_end'].append(time)

    for k in labels.keys():
        labels[k] = np.array(labels[k], dtype='datetime64[s]')
        
    events = determine_events(labels)
    return (events, labels)
