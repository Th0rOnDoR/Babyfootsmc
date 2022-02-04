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
from utils.drive import *
from processing_match import *
from processing_delmail import *
#from processing_drive import *




SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file'
          ]

def processing_drive():
    service = get_gdrive_service()
    main_folder = '19B8pLM-jO4F6YvlrZGP8S02PGCI6LEDo'
    main_folder_individual = '1KeClK1KHFt70ZMmOv9XxpMPd8DqD_HgX'
    today = str(date.today())
    print("[processing_drive]" + today)
    
    classement = get_classement()
    filename = "classement " + today + ".txt"
    print("[processing_drive] filename: " + filename)
    
    file = open(filename, "w")
    i = 0
    
    for i in range(len(classement)):
        classement[i][1] = str(classement[i][1])
        file.write(" ".join(classement[i]) + "\n")
    file.close()
    upload_files(filename, main_folder)
    print("[processing_drive] uploaded:" + filename + "  in: " + main_folder)
    if os.path.exists(filename):
        os.remove(filename)
        print("[processing_drive] deleting cache file " + filename)
    else:
        print("[processing_drive] The file does not exist")
    
    i = 0
    for i in range(len(classement)):
        folder_id = search_for_folder(classement[i][0])
        
        if folder_id == "false":
            folder_metadata = {
                "name": classement[i][0],
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [main_folder_individual]
            }
            folder = service.files().create(body=folder_metadata, fields="id").execute()
            folder_id = folder.get("id")
            filename = str(classement[i][0] + " " + today + ".txt")
            print("[processing_drive] creating cache file " + filename)
            file = open(filename, "w")
            classement[i][1] = str(classement[i][1])
            file.write(" ".join(classement[i]) + "\n")
            file.close()
            upload_files(filename, folder_id)
            print("[processing_drive] uploaded:" + filename + "  in: " + folder_id)
                
            if os.path.exists(filename):
                os.remove(filename)
                print("[processing_drive] deleting cache file " + filename)
            else:
                print("[processing_drive] The file does not exist")
        else: 
            filename = str(classement[i][0] + " " + today + ".txt")
            file = open(filename, "w")
            classement[i][1] = str(classement[i][1])
            file.write(" ".join(classement[i]) + "\n")
            file.close()
            print("[processing_drive] creating cache file " + filename)
            upload_files(filename, folder_id)
            print("[processing_drive] uploaded:" + filename + "  in: " + main_folder)
                    
            if os.path.exists(filename):
                os.remove(filename)
                print("[processing_drive] deleting cache file " + filename)
            else:
                print("[processing_drive] The file does not exist")
    print("[processing_drive] DONE")
