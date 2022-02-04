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

#from utils.mail import *
from utils.elo_utilities import *
from utils.drive import *
#from processing_match import *
#from processing_delmail import *
#from processing_drive import *
#Ask for all perms on this email
SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file'
          ]
our_email = 'babyfootsmc@gmail.com'





#GMAIL_AUTHENTICATE==================================================
def gmail_authenticate():
    
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
    print("[mail] " + "google_authenticate")
    return build('gmail', 'v1', credentials=creds)
#==================================================


#SEARCH_MESSAGE(service, str query)==================================================
def search_messages(service, query):
    '''
    query: str
    service: gmail_authenticate()
    '''
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages
#==================================================

#GET_SIZE_FORMAT(int nbe_bytes)==================================================
def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"
#==================================================


#CLEAN (str text)==================================================
def clean(text):
    # clean text for creating a folder
    print("[mail] " + "cleaning " + text) 
    return "".join(c if c.isalnum() else "_" for c in text)
    #==================================================


#PARSE_PARTS(service, parts, folder_name, message)==================================================
def parse_parts(service, parts, folder_name, message):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if part.get("parts"):
                # recursively call this function when we see that a part
                # has parts inside
                parse_parts(service, part.get("parts"), folder_name, message)
            if mimeType == "text/plain":
                # if the email part is text plain
                if data:
                    text = urlsafe_b64decode(data).decode()
                    print(text)
                    fichier = open("mail/" + str(folder_name) + "/info.txt", "a")
                    fichier.write(str("\n\n\nTexte:\n\n"))
                    fichier.write(text)
                    return text
            elif mimeType == "text/html":
                # if the email part is an HTML content
                # save the HTML file and optionally open it in the browser
                if not filename:
                    filename = "index.html"
                filepath = os.path.join("mail/" + folder_name, filename)
                
                print("Saving HTML to", filepath)
                with open(filepath, "wb") as f:
                    f.write(urlsafe_b64decode(data))
            else:
                # attachment other than a plain text or HTML
                for part_header in part_headers:
                    part_header_name = part_header.get("name")
                    part_header_value = part_header.get("value")
                    if part_header_name == "Content-Disposition":
                        if "attachment" in part_header_value:
                            # we get the attachment ID 
                            # and make another request to get the attachment itself
                            print("Saving the file:", filename, "size:", get_size_format(file_size))
                            attachment_id = body.get("attachmentId")
                            attachment = service.users().messages() \
                                        .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                            data = attachment.get("data")
                            filepath = os.path.join(folder_name, filename)
                            if data:
                                with open(filepath, "wb") as f:
                                    f.write(urlsafe_b64decode(data))
    #==================================================


#READ_MESSAGE(service, list return (search_mail)==================================================
def read_message(service, message):
    """
    This function takes Gmail API `service` and the given `message_id` and does the following:
        - Downloads the content of the email
        - Prints email basic information (To, From, Subject & Date) and plain/text parts
        - Creates a folder for each email based on the subject
        - Downloads text/html content (if available) and saves it under the folder created as index.html
        - Downloads any file that is attached to the email and saves it in the folder created
    """
    msg = service.users().messages().get(userId='me', id=message["id"], format='full').execute()
    # parts can be the message body, or attachments
    payload = msg['payload']
    headers = payload.get("headers")
    headers_save = []
    parts = payload.get("parts")
    folder_name = "email"
    print("="*50)
    has_subject = False
    if headers:
        # this section prints email basic info & creates a folder for the email
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == 'from':
                # we print the From address
                print("From:", value)
                headers_save.append(str("From: " + value + "\n"))
                sender = value 
            if name.lower() == "to":
                # we print the To address
                print("To:", value)
            if name.lower() == "subject":
                # make our boolean True, the email has "subject"
                headers_save.append(str("Subject: " + value + "\n"))
                has_subject = True
                # make a directory with the name of the subject
                folder_name = clean(value)
                # we will also handle emails with the same subject name
                folder_counter = 0
                if not os.path.exists("mail/"):
                    os.mkdir("mail/")
                while os.path.isdir("mail/" + folder_name):
                    folder_counter += 1
                    folder_name = str(clean(value) + "__" +  str(folder_counter))
                os.mkdir(str("mail/" + folder_name))
                #print("Subject:", value)    
            if name.lower() == "date":
                # we print the date when the message was sent
                print("Date:", value)
                headers_save.append(str("Date: " + value + "\n"))
    if not has_subject:
        # if the email does not have a subject, then make a folder with "email" name
        # since folders are created based on subjects
        if not os.path.isdir("mail/" + folder_name):
            os.mkdir(str("mail/" + folder_name))
    text = parse_parts(service, parts, folder_name, message)
    fichier = open("mail/" + str(folder_name) + "/info.txt", "w")
    fichier.write(str("\n".join(headers_save)))
    fichier.close()
    print("="*50) 
    return text, sender
    #==================================================

#build_message(str email, str objet, str body)==================================================
def build_message(destination, obj, body):  
    message = MIMEText(body)
    message['to'] = destination
    message['from'] = our_email
    message['subject'] = obj
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    #==================================================

#SEND_MESSAGE(servicd, str email , str obj, str body)==================================================
def send_message(service, destination, obj, body):
    print("[mail] " + "send message: " + "\n" + destination + "\n" + obj + "\n" + body)
    print("[mail] " + "message sended")
    return service.users().messages().send(userId="me",body=build_message(destination, obj, body)).execute()
    #==================================================

#DELETE_MESSAGE(service,str recherche)==================================================
def delete_messages(service, query):
    messages_to_delete = search_messages(service, query)
    # it's possible to delete a single message with the delete API, like this:
    # service.users().messages().delete(userId='me', id=msg['id'])
    # but it's also possible to delete all the selected messages with one query, batchDelete
    print("[mail] " + "deleting")
    return service.users().messages().batchDelete(
      userId='me',
      body={
          'ids': [ msg['id'] for msg in messages_to_delete]
      }
    ).execute()
    #==================================================

#==================================================   
def mark_as_unread(service, query):
    messages_to_mark = search_messages(service, query)
    return service.users().messages().batchModify(
        userId='me',
        body={
            'ids': [ msg['id'] for msg in messages_to_mark ],
            'addLabelIds': ['UNREAD']
        }
    ).execute()
    #==================================================


