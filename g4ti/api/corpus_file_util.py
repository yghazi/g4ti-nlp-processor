from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import g4ti.constants as constants


def google_auth():
    auth = GoogleAuth(settings_file=constants.DRIVE_AUTH_SETTINGS)
    auth.LoadCredentialsFile(constants.DRIVE_CREDS_FILE)
    if auth.credentials is None:
        # Authenticate if credentials.json not there
        # auth.CommandLineAuth()
        auth.LocalWebserverAuth()
        auth.SaveCredentialsFile(constants.DRIVE_CREDS_FILE)
    elif auth.access_token_expired:
        # Refresh them if expired
        auth.Refresh()
    else:
        # Initialize the saved creds
        auth.Authorize()
    return auth


def upload_file(folder_id, file):
    drive = GoogleDrive(google_auth())
    mime = dict(title=file, parents=[{"kind": "drive#fileLink", "id": folder_id}])
    _file = drive.CreateFile(mime)  # Create GoogleDriveFile instance with title 'Hello.txt'.
    _file.SetContentFile(file)


drive = GoogleDrive(google_auth())
mime = dict(title="HelloWorld.txt", parents=[{"kind": "drive#fileLink", "id": constants.DRIVE_RAWDOCS_FOLDER_ID}])
_file = drive.CreateFile(mime)  # Create GoogleDriveFile instance with title 'Hello.txt'.
_file.SetContentString('Hello World!')  # Set content of the file from given string.
_file.Upload()

# print('title: %s, id: %s' % (file1['title'], file1['id']))
#
# # Auto-iterate through all files in the root folder.
# file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
# for file1 in file_list:
#     print('title: %s, id: %s' % (file1['title'], file1['id']))
