""" Converts the epilepsy csv dataset into hdf5
"""
import glob
import radar.util.avro
import radar.io.hdf5

KCL_DIR = '/Users/callum/RADAR/Data/Epilepsy/KCL'
UKLFR_DIR = '/Users/callum/RADAR/Data/Epilepsy/UKLFR'

HDF_FILE = radar.io.hdf5.open_project('/Users/callum/RADAR/Data/Epilepsy.h5',
                                      mode='a')

KEY_SCHEMA_FILE = '/Users/callum/RADAR/RADAR-Schemas/commons/kafka/measurement_key.avsc'
VALUE_SCHEMAS_DIR = '/Users/callum/RADAR/RADAR-Schemas/commons/passive'

value_schemas_dict = {'android_'+source.split('/')[-1].split('.')[0]: source
                      for source in glob.glob(VALUE_SCHEMAS_DIR + '/*/*')}

with open(KEY_SCHEMA_FILE, 'r') as f:
    key_schema_json = f.read()


""" KCL Subjects """
"""
kcl_subjects = glob.glob(KCL_DIR+'/KCL[0-9][0-9]')
possible_subdirs = set(['E4', 'EMPATICA'])

for subject in kcl_subjects:
    subj_id = subject.split('/')[-1]
    print(subj_id)
    subdirs = glob.glob(subject+'/*')
    subdir_names = [sdir.split('/')[-1] for sdir in subdirs]
    data_subdir = list(set(subdir_names) & possible_subdirs)
    if data_subdir:
        subdirs = glob.glob(subject + '/' + data_subdir[0] + '/*')
    sources = [sdir.split('/')[-1] for sdir in subdirs]
    for i in range(len(sources)):
        if sources[i] in value_schemas_dict.keys():
            print(sources[i])
            with open(value_schemas_dict[sources[i]], 'r') as f:
                schema = radar.util.avro.RadarSchema(key_json=key_schema_json,
                                                     value_json=f.read())
            df = schema.load_csv_folder(subdirs[i])
            where = '/KCL/' + df['key.userId'][0]
            HDF_FILE.save_dataframe(df, where=where, name=sources[i])

"""
""" UKLFR Subjects """

lfr_subjects = glob.glob(UKLFR_DIR + '/UKLFR*')

for subj in lfr_subjects:
    subj_id = subj.split('/')[-1]
    print(subj_id)
    subdirs = glob.glob(subj+'/*')
    sources = [sdir.split('/')[-1] for sdir in subdirs]
    for i, source in enumerate(sources):
        try:
            if source in getattr(getattr(HDF_FILE.root, 'UKLFR'), subj_id):
                continue
        except:
            pass
        if source in value_schemas_dict:
            print(source)
            with open(value_schemas_dict[source], 'r') as f:
                schema = radar.util.avro.RadarSchema(key_json=key_schema_json,
                                                     value_json=f.read())
                try:
                    df = schema.load_csv_folder(subdirs[i])
                except OSError:
                    print('No CSV files in data folder: {}'.format(subdirs[i]))
                    continue
                where = '/UKLFR/' + df['key.userId'][0]
                HDF_FILE.save_dataframe(df, where=where, name=source)


HDF_FILE.close()
