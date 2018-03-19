#!/usr/bin/env python3
import glob
import radar.util.edf, radar.io.csv

KCL_DIR = ''

folders = glob.glob(KCL_DIR + 'KCL2*')

for folder in folders:
    print(folder.split('/')[-1])
    edf_files = glob.glob(folder + '/**/*.edf', recursive=True)
    anno, _ = radar.util.edf.parse_all_edf(edf_files)
    outfile = folder + '/' + folder.split('/')[-1] + '_annotations.csv'
    radar.io.csv.write_csv(anno, fname=outfile,
                           fieldnames=['onset real time (s)',
                                       'onset study time (s)',
                                       'duration (s)',
                                       'description'])
