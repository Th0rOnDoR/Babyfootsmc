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
from processing_drive import *

def main():

    print("Traitement matchs: match")
    print("Suppresion email: delmail")
    print("Mise à jour du drive: drive")
    cmd = input("Cmd ?")
    cmd = cmd.split(" ")
    
    if cmd[0] == "match":
        processing_match()
    
    if cmd[0] == "delmail":
        processing_delmail()
        
    if cmd[0] == "drive":
        processing_drive()
    if cmd[0] == "":
        processing_match()
        i = 0
        for i in range(0,30):
            print("waiting until 30 ;" + str(i))
            time.sleep(1)
        processing_delmail()
        i = 0
        for i in range(0,10):
            print("waiting until 10 ;" + str(i))
            time.sleep(1)
        processing_drive()
        print("\n\n\nFIN")
    
    


if __name__ == "__main__":
    main()
