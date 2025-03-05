# utils/google_drive.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from django.utils.timezone import now
from googleapiclient.http import MediaFileUpload
from accounts.models import GoogleDriveCredentials


def get_drive_service(user):
    """Initialize Google Drive service with credentials from the user's stored GoogleDriveCredentials."""

    try:
        # Fetch user credentials from DB
        credentials_obj = GoogleDriveCredentials.objects.filter(user=user).first()

        if not credentials_obj:
            raise Exception("No Google Drive credentials found for this user.")

        # Create Google credentials object
        creds = Credentials(
            token=credentials_obj.access_token,
            refresh_token=credentials_obj.refresh_token,
            client_id=credentials_obj.client_id,
            client_secret=credentials_obj.client_secret,
            scopes=["https://www.googleapis.com/auth/drive.file"],
            token_uri="https://oauth2.googleapis.com/token"
        )

        # Refresh the token if expired
        if credentials_obj.token_expiry and credentials_obj.token_expiry <= now():
            try:
                creds.refresh(Request())
                # Update the new access token and expiry in the database
                credentials_obj.access_token = creds.token
                credentials_obj.token_expiry = now() + creds.expiry
                credentials_obj.save()
            except Exception as e:
                raise Exception(f"Failed to refresh credentials: {str(e)}")

        return build('drive', 'v3', credentials=creds)

    except Exception as e:
        raise Exception(f"Error initializing Google Drive service: {str(e)}")


def create_folder(service, folder_name, parent_id=None):
    """Create a folder in Google Drive and return its ID."""
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        folder_metadata['parents'] = [parent_id]

    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')


def find_folder_by_date(service, date_str):
    """Search for a folder with the exact date (e.g., '2025-03-04')."""
    query = f"mimeType='application/vnd.google-apps.folder' '{date_str}'"
    try:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=10
        ).execute()
        folders = response.get('files', [])
        for folder in folders:
            if folder.get('name') == date_str:
                return folder.get('id')
    except Exception as e:
        print(f"Error searching for folder: {e}")
    return None


def upload_to_drive(user, file_path, file_name, folder_id):
    """Upload a file to Google Drive in the specified folder."""
    service = get_drive_service(user)

    # Determine mimetype based on file extension
    mimetype = 'text/plain' if file_name.endswith('.txt') else 'audio/mpeg' if file_name.endswith('.mp3') else 'application/octet-stream'

    # Define file metadata with the folder as parent
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    # Upload the file
    media = MediaFileUpload(file_path, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')