from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile

import g4ti.constants as constants

drive_auth_settings = constants.DRIVE_AUTH_SETTINGS
drive_credentials_file = constants.DRIVE_CREDS_FILE
auth = GoogleAuth(settings_file=drive_auth_settings)


def get_authentication_url():
    return auth.GetAuthUrl()


def set_authentication_code(code):
    is_auth = False
    try:
        auth.Auth(code)
        auth.SaveCredentialsFile(drive_credentials_file)
        is_auth = True
    except:
        print("Error occurred while trying to authenticate via given code: {0}".format(code))
    finally:
        return is_auth


def google_auth():
    auth.LoadCredentialsFile(drive_credentials_file)
    if auth.credentials is None:
        # Authenticate if credentials.json not there
        # auth.CommandLineAuth()
        # auth.LocalWebserverAuth()
        # custom_authentication_flow()
        print('Authenticate via this url: {0}'.format(auth.GetAuthUrl()))
        return None
    elif auth.access_token_expired:
        # Refresh them if expired
        auth.Refresh()
    else:
        # Initialize the saved creds
        auth.Authorize()
    return auth


def upload_file(folder_id, file_name, file):
    is_uploaded = False
    if google_auth() is not None:
        try:
            drive = GoogleDrive(auth)
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
    if google_auth() is not None:
        print("It's not..")
        drive = GoogleDrive(google_auth())
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
