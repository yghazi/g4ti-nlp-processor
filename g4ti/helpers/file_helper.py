import os
import traceback

from g4ti import constants
from g4ti.helpers.app_helper import AppHelper
from g4ti.helpers.config_helper import ConfigHelper
from g4ti.helpers.drive_helper import DriveHelper


class FileHelper:
    def __init__(self):
        self.config_helper = ConfigHelper()
        self.drive_helper = DriveHelper()
        self.app_helper = AppHelper()
        self.create_dir_if_not_exists(self.config_helper.TRAIN_DATA_PATH)
        self.create_dir_if_not_exists(self.config_helper.RAW_DATA_PATH)

    def create_dir_if_not_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_file(self, file_name, file_content, train=True):
        if file_content is not None:
            drive_folder = constants.DRIVE_CORPUS_FOLDER_ID
            path = self.config_helper.TRAIN_DATA_PATH
            ext = '.tsv'
            if not train:
                drive_folder = constants.DRIVE_RAWDOCS_FOLDER_ID
                path = self.config_helper.RAW_DATA_PATH
                ext = '.txt'
        file_path = path + os.sep + file_name + ext
        # write temporarily to the folder
        with open(file_path, 'w') as f:
            f.write(file_content)
        try:
            if self.drive_helper.upload_file(drive_folder, file_name + ext, file_path):
                print("File %s uploaded" % file_name + ext)
                # TODO: OK to remove file, when in production
                # os.remove(file_path)
                # check for pending uploads, if 15 min have passed since last
                # check
                if (self.app_helper.current_milli_time() - self.config_helper.last_pending_check) > 900000:
                    self.upload_pending_files(path, drive_folder)
        except:
            print(traceback.format_exc())
            # TODO save request in case of failure
