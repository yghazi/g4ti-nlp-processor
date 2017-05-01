import hashlib
import time


class AppHelper:
    def __init__(self):
        self.digest = hashlib.md5()

    def current_milli_time(self):
        """
        Get current system time in milliseconds
        :return: system time in milliseconds
        """
        return round(time.time() * 1000)

    def get_file_name(self, content):
        """ Get file name by caclulating content hash """
        self.digest.update(content.encode('utf-8'))
        return self.digest.hexdigest()