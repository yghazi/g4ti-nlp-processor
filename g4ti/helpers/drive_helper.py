from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import g4ti.constants as constants


class DriveHelper:
    def __init__(self):
        self.drive_auth_settings = constants.DRIVE_AUTH_SETTINGS
        self.drive_credentials_file = constants.DRIVE_CREDS_FILE
        self.auth = GoogleAuth(settings_file=self.drive_auth_settings)

    def get_authentication_url(self):
        return self.auth.GetAuthUrl()

    def set_authentication_code(self, code):
        is_auth = False
        try:
            self.auth.Auth(code)
            self.auth.SaveCredentialsFile(self.drive_credentials_file)
            is_auth = True
        except:
            print("Error occurred while trying to authenticate via given code: {0}".format(code))
        finally:
            return is_auth

    def google_auth(self):
        self.auth.LoadCredentialsFile(self.drive_credentials_file)
        if self.auth.credentials is None:
            # Authenticate if credentials.json not there
            # auth.CommandLineAuth()
            # auth.LocalWebserverAuth()
            # custom_authentication_flow()
            print('Authenticate via this url: {0}'.format(self.auth.GetAuthUrl()))
            return None
        elif self.auth.access_token_expired:
            # Refresh them if expired
            self.auth.Refresh()
        else:
            # Initialize the saved creds
            self.auth.Authorize()
        return self.auth

    def upload_file(self, folder_id, file_name, file):
        is_uploaded = False
        if self.google_auth() is not None:
            try:
                drive = GoogleDrive(self.auth)
                mime = dict(title=file_name, parents=[{"kind": "drive#fileLink", "id": folder_id}])
                _file = drive.CreateFile(mime)  # Create GoogleDriveFile instance with title 'Hello.txt'.
                _file.SetContentFile(file)
                _file.Upload()
                is_uploaded = True
            except:
                print("Something ugly happened.. Couldn't upload file")
            finally:
                return is_uploaded

        print('Check to see if auth is none...')

        if self.google_auth() is not None:
            print("It's not..")
            drive = GoogleDrive(self.google_auth())
            mime = dict(title="HelloWorld.txt",
                        parents=[{"kind": "drive#fileLink", "id": constants.DRIVE_RAWDOCS_FOLDER_ID}])
            _file = drive.CreateFile(mime)  # Create GoogleDriveFile instance with title 'Hello.txt'.
            _file.SetContentString('Hello World!')  # Set content of the file from given string.
            _file.Upload()


            # print('title: %s, id: %s' % (file1['title'], file1['id']))
            #
            # # Auto-iterate through all files in the root folder.
            # file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
            # for file1 in file_list:
            #     print('title: %s, id: %s' % (file1['title'], file1['id']))
