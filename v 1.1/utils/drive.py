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

from utils.cte import *
from utils.logs import *
    
#SHOW_FILES_ACCES(int number of file to show)==================================================
def show_files_acces(service, n):
    """
    even if this is never used, could be usefull one day
    :service:
    :int n: list of file to show
    """
    #  the Drive v3 API
    results = service.files().list(
        pageSize=n, fields="nextPageToken, files(id, name, mimeType, size, parents, modifiedTime)").execute()
    # get the results
    items = results.get('files', [])
    # list all n files & folders
    list_files(items)
    #==================================================

#LIST_FILES(items)==================================================  
def list_files(items):
    '''
    given items returned by Google Drive API, prints them in a tabular way
    useless to but..
    '''
    if not items:
        # empty drive
        add_logs(1, '[utils.drive] list_files: No files found.')
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
        add_logs(0,"[utils.drive] list_files: Files:")
        # convert to a human readable table
        table = tabulate(rows, headers=["ID", "Name", "Parents", "Size", "Type", "Modified Time"])
        # print the table
        print(table)
        #==================================================

#UPLOAD_FILES(str filename, str folder_id if none, root)==================================================
def upload_files(service, file_name, folder_id):
    """
    upload a file to the folder id
    :service: 
    :str file_name: the name of the file you want to upload
    :str folder_id: the id of the folder you want to upload the file in, if none folder have this id, file will be upload in root
    """
    # authenticate account
    file_metadata = {
        "name": file_name,
        "parents": [folder_id],
    }
    add_logs(0,"[utils.drive] upload_files " + str(file_metadata))
    # upload
    media = MediaFileUpload(file_name, resumable=True)
    add_logs(0,"[utils.drive] upload_files: Uploading:" + file_name)
    #file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    #add_logs(0,"[utils.drive] upload_files: File created, id:" + file.get("id"))
    #==================================================


#SEARCH_FOR_FOLDER(str foldername to search for)==================================================
def search_for_folder(service, foldername):
    """
    search for folder only
    :service:
    :str foldername: the name of the folder you look for
    """
    page_token = None
    #searching every folder
    response = service.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name, mimeType)',
                                    pageToken=page_token).execute()
    add_logs(0,str(response))
    for file in response.get('files', []):
        add_logs(0,"[utils.drive] Search_for_folder: folder_name: " + file.get('name'))
        if file.get('name') == foldername:
            #trying if any folder, anywhere have the same name as the folder you look for
            #WARNING, the folder can be in trash 
            add_logs(0,"[utils.drive] search_for_folder: " + file.get('id'))
            return file.get('id')
    return 'false' #if no file correspond
    #==================================================

#SEARCH (service, str search)==================================================
def search(service, query):
    """
    search of anything
    :service:
    :str query: name you want to search for. Note: could be use to search for file or everything, see google drive doc to userstand
    """
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
def search_for_files(service, filetype):
    """
    search for a type of only
    :service:
    :str filetype: type of file you look for, cant be anything like for search
    """
    # filter to text files
    #filetype = "text/plain"
    # search for files that has type of text/plain
    search_result = search(service, query=f"mimeType='{filetype}'")
    # convert to table to print well
    table = tabulate(search_result, headers=["ID", "Name", "Type"])
    add_logs(0,"[utils.drive] search_for_files: ")
    print(table)
    #==================================================


#DOWNLOAD_FILES_FROM_GOOGLE_DRIVE(id, str destination)==================================================
def download_file_from_google_drive(service, id, destination):
    """
    download specific file from google drive to a special location
    :service:
    :str id: the id of the file you want to download
    :str destination: the path where you want to put the file
    """
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
        add_logs(0,"[utils.drive] download_file_from_google_drive: [+] File size:", file_size)
        add_logs(0,"[utils.drive] download_file_from_google_drive: [+] File name:", filename)
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
    add_logs(0,"[utils.drive] download_file_from_google_drive: [+] Downloading ", response.url)
    # get confirmation token
    token = get_confirm_token(response)
    if token:
        params = {'id': id, 'confirm':token}
        response = session.get(URL, params=params, stream=True)
    # download to disk
    save_response_content(response, destination)  
    #==================================================

#DOWNLOAD(str Filename)==================================================
def download(service, filename):
    """
    download a file
    :service:
    :str filename: name of the file you want to download
    """
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
