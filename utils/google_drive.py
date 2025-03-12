# utils/google_drive.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.utils.timezone import now
from googleapiclient.http import MediaFileUpload
from accounts.models import GoogleDriveCredentials
import re

import re



def find_surrat_folder(service):
    """Find the folder named 'Surrat data' in Google Drive."""
    query = "mimeType='application/vnd.google-apps.folder' and name='Surrat data'"
    try:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1  # We only need one
        ).execute()
        folders = response.get('files', [])
        return folders[0]['id'] if folders else None
    except Exception as e:
        print(f"Error searching for 'Surrat data' folder: {e}")
    return None



import re

def get_last_file_number(service, folder_id):
    """Retrieve the highest numbered file in the 'Surrat data' folder."""
    try:
        response = service.files().list(
            q=f"'{folder_id}' in parents and (name contains '.txt' or name contains '.mp3')",
            spaces='drive',
            fields='files(name)',
            pageSize=1000  # Fetch up to 1000 files
        ).execute()

        files = response.get('files', [])
        numbers = []

        # Extract numbers from filenames (e.g., 10000.txt, 10001.mp3)
        pattern = re.compile(r"(\d+)\.(txt|mp3)")
        for file in files:
            match = pattern.search(file.get('name'))
            if match:
                numbers.append(int(match.group(1)))  # Extract number part

        return max(numbers) if numbers else 9999  # Start from 10000 if no files exist

    except Exception as e:
        print(f"Error retrieving last file number: {e}")
        return 9999  # Default to 9999 so next starts at 10000




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


# def find_folder_by_date(service, date_str):
#     """Search for a folder with the exact date (e.g., '2025-03-04')."""
#     query = f"mimeType='application/vnd.google-apps.folder' '{date_str}'"
#     try:
#         response = service.files().list(
#             q=query,
#             spaces='drive',
#             fields='files(id, name)',
#             pageSize=10
#         ).execute()
#         folders = response.get('files', [])
#         for folder in folders:
#             if folder.get('name') == date_str:
#                 return folder.get('id')
#     except Exception as e:
#         print(f"Error searching for folder: {e}")
#     return None
def find_folder_by_date(service, date_str):
    """Search for a folder with the exact date (e.g., '2025-03-04')."""
    query = f"mimeType='application/vnd.google-apps.folder' and name='{date_str}'"
    try:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1  # We need only one folder
        ).execute()
        folders = response.get('files', [])
        return folders[0]['id'] if folders else None
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


# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from django.utils.timezone import now
# from accounts.models import GoogleDriveCredentials
# import re
#
#
# def get_drive_service(user):
#     """Initialize Google Drive service with credentials from the user's stored GoogleDriveCredentials."""
#     try:
#         credentials_obj = GoogleDriveCredentials.objects.filter(user=user).first()
#         if not credentials_obj:
#             raise Exception("No Google Drive credentials found for this user.")
#
#         creds = Credentials(
#             token=credentials_obj.access_token,
#             refresh_token=credentials_obj.refresh_token,
#             client_id=credentials_obj.client_id,
#             client_secret=credentials_obj.client_secret,
#             scopes=["https://www.googleapis.com/auth/drive.file"],
#             token_uri="https://oauth2.googleapis.com/token"
#         )
#
#         if credentials_obj.token_expiry and credentials_obj.token_expiry <= now():
#             try:
#                 creds.refresh(Request())
#                 credentials_obj.access_token = creds.token
#                 credentials_obj.token_expiry = creds.expiry
#                 credentials_obj.save()
#             except Exception as e:
#                 raise Exception(f"Failed to refresh credentials: {str(e)}")
#
#         return build('drive', 'v3', credentials=creds)
#     except Exception as e:
#         raise Exception(f"Error initializing Google Drive service: {str(e)}")
#
#
# def create_folder(service, folder_name, parent_id=None):
#     """Create a folder in Google Drive and return its ID."""
#     folder_metadata = {
#         'name': folder_name,
#         'mimeType': 'application/vnd.google-apps.folder'
#     }
#     if parent_id:
#         folder_metadata['parents'] = [parent_id]
#     folder = service.files().create(body=folder_metadata, fields='id').execute()
#     return folder.get('id')
#
#
# def find_or_create_folder(service, folder_name):
#     """Find an existing folder by name or create it if it doesn't exist."""
#     query = f"mimeType='application/vnd.google-apps.folder' '{folder_name}'"
#     try:
#         response = service.files().list(
#             q=query,
#             spaces='drive',
#             fields='files(id, name)',
#             pageSize=10
#         ).execute()
#         folders = response.get('files', [])
#         for folder in folders:
#             if folder.get('name') == folder_name:
#                 print(f"Using existing folder: {folder_name} (ID: {folder.get('id')})")
#                 return folder.get('id')
#         # If not found, create it
#         print(f"Creating new folder: {folder_name}")
#         return create_folder(service, folder_name)
#     except Exception as e:
#         print(f"Error finding folder: {e}")
#         return create_folder(service, folder_name)  # Fallback to creation
#
#
# def get_last_file_number(service, folder_id):
#     """Find the highest numbered file in the specified folder (e.g., 10003 from '10003.txt' or '10003.mp3')."""
#     try:
#         query = f"'{folder_id}' in parents"
#         response = service.files().list(
#             q=query,
#             spaces='drive',
#             fields='files(name)',
#             pageSize=1000
#         ).execute()
#         files = response.get('files', [])
#
#         max_number = None
#         pattern = re.compile(r'(\d+)\.(txt|mp3)')
#         for file in files:
#             match = pattern.match(file['name'])
#             if match:
#                 number = int(match.group(1))
#                 if max_number is None or number > max_number:
#                     max_number = number
#         return max_number
#     except Exception as e:
#         print(f"Error finding last file number: {e}")
#         return None
#
#
# def upload_to_drive(user, file_path, file_name, folder_id):
#     """Upload a file to Google Drive in the specified folder."""
#     service = get_drive_service(user)
#     mimetype = 'text/plain' if file_name.endswith('.txt') else 'audio/mpeg' if file_name.endswith(
#         '.mp3') else 'application/octet-stream'
#     file_metadata = {
#         'name': file_name,
#         'parents': [folder_id]
#     }
#     media = MediaFileUpload(file_path, mimetype=mimetype)
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file.get('id')