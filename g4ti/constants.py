import os

SEP = os.sep
G4TI_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
BASE_DIR = os.path.abspath(os.path.join(G4TI_DIR, os.pardir))
TRAIN_MODEL = BASE_DIR + SEP + 'model' + SEP + 'g4ti-chunker.pickle'
DRIVE_AUTH_SETTINGS = BASE_DIR + SEP + 'conf' + SEP + 'drive-auth-settings.yaml'
DRIVE_CREDS_FILE = BASE_DIR + SEP + 'conf' + SEP + 'credentials.json'

G4TI_TRAINING_DIR = BASE_DIR + SEP + 'g4ti-corpus' + SEP + 'train'
G4TI_RAW_DIR = BASE_DIR + SEP + 'g4ti-corpus' + SEP + 'raw'
TEST_DIR = BASE_DIR + SEP + 'test'

# TODO: change back to what they were...
DRIVE_CORPUS_FOLDER_ID = '0B5fRb4nvaiFHLXZLRVBpU01WYWs'
DRIVE_RAWDOCS_FOLDER_ID = '0B5fRb4nvaiFHV1AzYlJuaHhyMms'
