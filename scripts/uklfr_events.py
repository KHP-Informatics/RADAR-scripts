import util.parsers
import glob
import numpy as np

UKFLR_DIR = '/Users/callum/RADAR/Data/Epilepsy/UKLFR'

for csv in glob.glob(UKFLR_DIR + '/*/*_ext.csv'):
    folder = '/'.join(csv.split('/')[:-1])
    with open(csv, 'r') as f:
        events, labels = util.parsers.uklfr_subject_ext_csv(f)
    np.savetxt(folder+'/events.csv', events.astype(np.int64),
               header='clin_start, clin_end, eeg_start, eeg_end',
               delimiter=',')
