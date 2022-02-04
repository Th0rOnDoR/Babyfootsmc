import pickle
import os
import re
import io
import requests
import time
from datetime import date
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from base64 import urlsafe_b64decode, urlsafe_b64encode
from tqdm import tqdm
from tabulate import tabulate

from utils.mail import *
from utils.elo_utilities import *
#from utils.drive import *
#from processing_match import *
#from processing_delmail import *
#from processing_drive import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://mail.google.com/'
          ]

#GET_GDRIVE_SERVICE==================================================
def get_gdrive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    print("[drive] get_gdrive_service")
    return build('drive', 'v3', credentials=creds)
    #==================================================
    
    
#SHOW_FILES_ACCES(int number of file to show)==================================================
def show_files_acces(n):
    service = get_gdrive_service()
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=n, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)").execute()
    # get the results
    items = results.get('files', [])
    # list all n files & folders
    list_files(items)
    #==================================================

#LIST_FILES(items)==================================================  
def list_files(items):
    """given items returned by Google Drive API, prints them in a tabular way"""
    if not items:
        # empty drive
        print('No files found.')
    else:
        rows = []
        for item in items:
            # get the File ID
            id = item["id"]
            # get the name of file
            name = item["name"]
            try:
                # parent directory ID
                parents = item["parents"]
            except:
                # has no parrents
                parents = "N/A"
            try:
                # get the size in nice bytes format (KB, MB, etc.)
                size = get_size_format(int(item["size"]))
            except:
                # not a file, may be a folder
                size = "N/A"
            # get the Google Drive type of file
            mime_type = item["mimeType"]
            # get last modified date time
            modified_time = item["modifiedTime"]
            # append everything to the list
            rows.append((id, name, parents, size, mime_type, modified_time))
        print("Files:")
        # convert to a human readable table
        table = tabulate(rows, headers=["ID", "Name", "Parents", "Size", "Type", "Modified Time"])
        # print the table
        print(table)
        #==================================================

#UPLOAD_FILES(str filename, str folder_id if none, root)==================================================
def upload_files(file_name, folder_id):
    """
    Creates a folder and upload a file to it
    """
    # authenticate account
    service = get_gdrive_service()
    file_metadata = {
        "name": file_name,
        "parents": [folder_id],
    }
    print("[drive] " + str(file_metadata))
    # upload
    media = MediaFileUpload(file_name, resumable=True)
    print("[drive] Uploading:" + file_name)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("[drive] File created, id:", file.get("id"))
    #==================================================


#SEARCH_FOR_FOLDER(str foldername to search for)==================================================
def search_for_folder(foldername):
    page_token = None
    service = get_gdrive_service()

    response = service.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name, mimeType)',
                                    pageToken=page_token).execute()
    print(str(response))
    #print('resp')
    for file in response.get('files', []):
        print("[drive] Search for folder:" + file.get('name'))
        if file.get('name') == foldername:
            print(file.get('id'))
            return file.get('id')
    return 'false'
    #==================================================

#SEARCH (service, str search)==================================================
def search(service, query):
    # search for the file
    result = []
    page_token = None
    while True:
        response = service.files().list(q=query,
                                        spaces="drive",
                                        fields="nextPageToken, files(id, name, mimeType)",
                                        pageToken=page_token).execute()
        # iterate over filtered files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more files
            break
    return result
    #==================================================

#SEARCH_FOR_FILES(str filetype)==================================================
def search_for_files(filetype):
    # filter to text files
    #filetype = "text/plain"
    
    # authenticate Google Drive API
    service = get_gdrive_service()
    # search for files that has type of text/plain
    search_result = search(service, query=f"mimeType='{filetype}'")
    # convert to table to print well
    table = tabulate(search_result, headers=["ID", "Name", "Type"])
    print(table)
    #==================================================


#DOWNLOAD_FILES_FROM_GOOGLE_DRIVE(id, str destination)==================================================
def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        # get the file size from Content-length response header
        file_size = int(response.headers.get("Content-Length", 0))
        # extract Content disposition from response headers
        content_disposition = response.headers.get("content-disposition")
        # parse filename
        filename = re.findall("filename=\"(.+)\"", content_disposition)[0]
        print("[+] File size:", file_size)
        print("[+] File name:", filename)
        progress = tqdm(response.iter_content(CHUNK_SIZE), f"Downloading {filename}", total=file_size, unit="Byte", unit_scale=True, unit_divisor=1024)
        with open(destination, "wb") as f:
            for chunk in progress:
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # update the progress bar
                    progress.update(len(chunk))
        progress.close()

    # base URL for download
    URL = "https://docs.google.com/uc?export=download"
    # init a HTTP session
    session = requests.Session()
    # make a request
    response = session.get(URL, params = {'id': id}, stream=True)
    print("[+] Downloading", response.url)
    # get confirmation token
    token = get_confirm_token(response)
    if token:
        params = {'id': id, 'confirm':token}
        response = session.get(URL, params=params, stream=True)
    # download to disk
    save_response_content(response, destination)  
    #==================================================

#DOWNLOAD(str Filename)==================================================
def download(filename):
    service = get_gdrive_service()
    # the name of the file you want to download from Google Drive 
    #filename = "bbc.zip"
    # search for the file by name
    search_result = search(service, query=f"name='{filename}'")
    # get the GDrive ID of the file
    file_id = search_result[0][0]
    # make it shareable
    service.permissions().create(body={"role": "reader", "type": "anyone"}, fileId=file_id).execute()
    # download file
    download_file_from_google_drive(file_id, filename)
    #==================================================
