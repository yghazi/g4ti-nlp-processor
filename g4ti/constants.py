import os

G4TI_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
BASE_DIR = os.path.abspath(os.path.join(G4TI_DIR, os.pardir))
TRAIN_MODEL = BASE_DIR + os.sep + 'model' + os.sep + 'g4ti-chunker.pickle'
DRIVE_AUTH_SETTINGS = BASE_DIR + os.sep + 'conf' + os.sep + 'drive-auth-settings.yaml'
DRIVE_CREDS_FILE = BASE_DIR + os.sep + 'conf' + os.sep + 'credentials.json'

G4TI_TRAINING_DIR = BASE_DIR + os.sep + 'g4ti-corpus' + os.sep + 'train'
G4TI_RAW_DIR = BASE_DIR + os.sep + 'g4ti-corpus' + os.sep + 'raw'
TEST_DIR = BASE_DIR + os.sep + 'test'

DRIVE_CORPUS_FOLDER_ID = '0B5fRb4nvaiFHZk00YURodU13LTQ'
DRIVE_RAWDOCS_FOLDER_ID = '0B5fRb4nvaiFHZVg5MEFCaEM2ZWM'
