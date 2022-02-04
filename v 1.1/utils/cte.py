import os
import pickle
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def default_version():
    return '1.0'

def default_search():
    return 'Subject:test in:inbox'

def default_end():
    '''
    Utility fonction that returns the default ending of an email
    '''
    body = "\n\nLien vers le drive du classement:\n https://drive.google.com/drive/folders/19B8pLM-jO4F6YvlrZGP8S02PGCI6LEDo?usp=sharing \nLien vers la Foire Aux Questions: https://docs.google.com/document/d/102unm8PoZUGEre5bUmgqltmF_D8rKDu_Mxp1imE4yJo/edit \n\nContact: t.courrege@smctab.com\nMessage auto-généré, veuillez voir la FAQ sur le drive\nDéveloppeur et propriétaire: TCourrege\n"
    return body
    
def default_addacc_search():
    return "Subject:ADDACC in:inbox"
    
def default_delacc_search():
    return "Subject:DELACC in:inbox"
    
def id_main_folder():
    return '19B8pLM-jO4F6YvlrZGP8S02PGCI6LEDo'

def id_score_folder():
    return '1KeClK1KHFt70ZMmOv9XxpMPd8DqD_HgX'

def id_classement_folder():
    return '1xMXwyHcrJhGfVUzQQdKYJpsphy2d9gLB'
    
def service_gmail():
    SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file'
          ]
    our_email = 'babyfootsmc@gmail.com'
    creds = None
        # the file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def service_drive():
    '''
    get google service service, its the same as gmail but dont care
    '''
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
    return build('drive', 'v3', credentials=creds)




