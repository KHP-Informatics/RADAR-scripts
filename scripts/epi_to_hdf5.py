import util.avro, util.hdf5
import glob
import h5py

KCL_DIR = ''
UKLFR_DIR = ''

HDF_FILE = h5py.File('')

KEY_SCHEMA_FILE = 'commons/kafka/measurement_key.avsc'
VALUE_SCHEMAS_DIR = 'commons/passive'

value_schemas_dict = {'android_'+source.split('/')[-1].split('.')[0]: source
                      for source in glob.glob(VALUE_SCHEMAS_DIR + '/*/*')}

with open(KEY_SCHEMA_FILE, 'r') as f:
    key_schema_json = f.read()


""" KCL Subjects """
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
                schema = util.avro.RadarSchema(key_json=key_schema_json,
                                               value_json=f.read())
            df = schema.load_csv_folder(subdirs[i])
            util.hdf5.append_hdf5(dataframe=df, hdf5=HDF_FILE,
                                  user_id='KCL/'+subj_id+'/raw',
                                  source=sources[i])
