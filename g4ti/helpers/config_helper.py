import re
import time

from g4ti import constants


class ConfigHelper:
    def __init__(self):
        self.TRAIN_DATA_PATH = constants.G4TI_TRAINING_DIR
        self.RAW_DATA_PATH = constants.G4TI_RAW_DIR
        self.TEST_PATH = constants.TEST_DIR
        self.TRAIN_MODEL_PICKLE = constants.TRAIN_MODEL
        self.last_pending_check = round(time.time() * 1000)
        self.tokenizer_troublesome_tags = ["REGKEY", "URL", "DOMAIN", "FILE"]
        self.IP_PATTERN = re.compile(
            '((?<![0-9])(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})[.](?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(?![0-9]))')
        self.EMAIL_PATTERN = re.compile(
            '((?:[a-zA-Z0-9.]+)@(?:[a-z]+.)(?:[a-z]{2,62}.[a-z]{2}|[a-z]{2,62}))')
        self.REGKEY_PATTERN = re.compile('((?:[HK][A-Z\_]+|[A-Z]+)\+\s+(?:.*)\+[a-zA-Z]+)')
        self.URL_PATTERN = re.compile(
            '(?:[a-z0-9\-]+\.)(?:[a-z]{2,18}\.[a-z]{2}|[a-z]{2,18})')
        self.DOMAIN_PATTERN = re.compile(
            '[a-zA-Z0-9\_\-]+(?:\.|\[(?:dot|\.)])+[a-zA-Z+\.\[\]]+')
        self.CVE_PATTERN = re.compile('CVE-\d{4}-\d{4}')
        self.HASH_PATTERN = re.compile('[a-fA-F0-9]')
        self.annotator_troublesome_tags = ["REGKEY", "URL", "DOMAIN", "FILE"]


