import os
import pickle
from math import sqrt
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
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
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()
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
                sender = value 
            if name.lower() == "to":
                # we print the To address
                print("To:", value)
            if name.lower() == "subject":
                # make our boolean True, the email has "subject"
                has_subject = True
                # make a directory with the name of the subject
                folder_name = clean(value)
                # we will also handle emails with the same subject name
                folder_counter = 0
                if not os.path.exists("mail/"):
                    os.mkdir("mail/")
                while os.path.isdir("mail/" + folder_name):
                    folder_counter += 1
                    # we have the same folder name, add a number next to it
                    if str("mail/" + folder_name[-1]).isdigit() and str("mail/" + folder_name[-2]) == "mail/_":
                        folder_name = f"{folder_name[:-2]}_{folder_counter}"
                    elif str("mail/" + folder_name[-2:]).isdigit() and str("mail/" + folder_name[-3]) == "_":
                        folder_name = f"{folder_name[:-3]}_{folder_counter}"
                    else:
                        folder_name = f"{folder_name}_{folder_counter}"
                os.mkdir(str("mail/" + folder_name))
                #print("Subject:", value)    
            if name.lower() == "date":
                # we print the date when the message was sent
                print("Date:", value)
    if not has_subject:
        # if the email does not have a subject, then make a folder with "email" name
        # since folders are created based on subjects
        if not os.path.isdir("mail/" + folder_name):
            os.mkdir(str("mail/" + folder_name))
    text = parse_parts(service, parts, folder_name, message)
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
    return service.users().messages().send(userId="me",body=build_message(destination, obj, body)).execute()
#==================================================



#excepted(int score_A, int score_B)==================================================
def excepted(A, B):
    return 1/(1+10**((B-A)/400))
#==================================================


#elo(int previous_elo_A, int previous_elo_B, int state_for_A)=================
def elo(elo_A, elo_B, state_for_A):
    k = 20
    return (k*(state_for_A - excepted(elo_A, elo_B)))
#==================================================
    
#GET_CLASSEMENT==================================================
def get_classement():
    classement = []
    fichier = open('elo.py', 'r')
    for ligne in fichier:
        if not ligne == "\n":
            classement.append(ligne)
    fichier.close()
    i = 0
    for i in range(len(classement)):
        x = 0
        x = classement[i]
        x = str(x).split(" ")
        y = x[-1] 
        x[-1] = y.split("\n")[0]
        x[-1] = int(x[-1])
        classement[i] = []
        classement[i] = x 
    return classement
#==================================================

#==================================================
def get_elo(target):
    classement = get_classement()
    i = 0
    elo_target = 0
    print(target)
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            elo_target = int(classement[i][1])
            return elo_target
    
    fichier = open('elo.py', 'a')
    fichier.write(str(target + ' 1000\n'))
    print("[New Player added] " + target)
    fichier.close()
    return 1000
#==================================================


#==================================================
def set_elo(target, elo):
    classement = get_classement()
    i = 0
    elo_target = 0
    for i in range(len(classement)):
        classement = get_classement()
        if str(classement[i][0]) == str(target): 
            classement[i][1] = str(str(elo) + "\n")
            fichier = open('elo.py', 'w')
            j = 0
            for j in range(len(classement)):
                
                classement[j][1] = str(classement[j][1])
                print(classement[j])
                classement_save = " ".join(classement[j])
                fichier.write(str(classement[j][0] + " " + str(classement[j][1]) +"\n"))
            fichier.close()
    return   
#==================================================

#==================================================
def match(Player, player_Score, Team_1, Team_2):
    player_Elo = get_elo(Player)
    if player_Score == "V":
        player_Score = 1
    elif player_Score == "D":
        player_Score = 0
    player_Elo += elo(Team_1, Team_2,player_Score)
    set_elo(Player, int(player_Elo))
    return
#==================================================

#DELETE_MESSAGE(service, str query)==================================================
def delete_messages(service, query):
    messages_to_delete  = search_messages(service, query)
    # it's possible to delete a single message with the delete API, like this:
    for msg in messages_to_delete:
        service.users().messages().trash(userId='me', id=msg['id'])
    # but it's also possible to delete all the selected messages with one query, batchDelete
    '''
    return service.users().messages().batchDelete(
      userId='me',
      body={
          'ids': [ msg['id'] for msg in messages_to_delete]
      }
    ).execute()
    '''
#==================================================

#==================================================
def team_elo(Player_A_Elo, Player_B_Elo):
    
        
    team_elo = (1.2*max(Player_A_Elo, Player_B_Elo)+min(Player_A_Elo, Player_B_Elo))/2
    return team_elo
#==================================================

#==================================================
def clean_name(string):
    string = string.replace("î", "i")
    string = string.replace("é", "e")
    string = string.replace("è", "e")
    string = string.replace("ï", "i")
    string = string.replace("ö", "o")
    return string
    #==================================================


senders = []
contenu_mail = []
# get emails that match the query you specify
results = search_messages(service, "is:unread Subject:CLASSEMENT in:inbox")  
# for each email matched, read it (output plain/text to console & save HTML and attachments)
for msg in results:
    contenu, sender = read_message(service, msg)
    #changing sendee
    sender = sender.split(" ")
    if not sender[-1] == 'babyfootsmc@gmail.com':
        senders.append(sender[-1])
        contenu_mail.append(contenu)
    
   
i = 0 
L_match = [] 
classement = []

#print(senders)
#print(contenu_mail)

 
for i in range(len(contenu_mail)):
    match_str = str(contenu_mail[i])
    match_list = match_str.split("\r\n")
    #print(match_list)
    if match_list[-1] == '':
        match_list.remove('')
    if len(match_list) == 4:
        player_A, player_A_Score = match_list[0].split(" ")
        player_B, player_B_Score = match_list[1].split(" ")
        player_C, player_C_Score = match_list[2].split(" ")
        player_D, player_D_Score = match_list[3].split(" ")
        
        
        player_A = clean_name(player_A)
        player_B = clean_name(player_B)
        player_C = clean_name(player_C)
        player_D = clean_name(player_D)
        
        player_A_Elo = get_elo(player_A)
        player_B_Elo = get_elo(player_B)
        player_C_Elo = get_elo(player_C)
        player_D_Elo = get_elo(player_D)        
        Team_1_Elo = team_elo(player_A_Elo, player_B_Elo)
        Team_2_Elo = team_elo(player_C_Elo, player_D_Elo)
        
        print(Team_1_Elo)
        print(Team_2_Elo)
        match(player_A, player_A_Score, Team_1_Elo, Team_2_Elo)
        match(player_B, player_B_Score, Team_1_Elo, Team_2_Elo)
        match(player_C, player_C_Score, Team_2_Elo, Team_1_Elo)
        match(player_D, player_D_Score, Team_2_Elo, Team_1_Elo)
    else:     
        send_message(service, senders[i], "Elo Rating SMC Program", "Format invalide pour l'email\n" + str(match_list))
    
    
delete = input("delete ?")
if delete == "Y":
    delete_messages(service, "CLASSEMENT")

print("done")
    
