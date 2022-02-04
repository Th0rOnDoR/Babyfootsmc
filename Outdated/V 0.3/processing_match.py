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
#from processing_match import *
#from processing_delmail import *
#from processing_drive import *


def processing_match():
    service = gmail_authenticate()
    senders = []
    contenu_mail = []
    results = search_messages(service, "Subject:TEST in:inbox")  
    for msg in results:
        contenu, sender = read_message(service, msg)
        sender = sender.split(" ")
        if not sender[-1] == 'babyfootsmc@gmail.com':
            senders.append(sender[-1])
            contenu_mail.append(contenu)
    i = 0 
    L_match = [] 
    classement = []
    print("[processing_match] " + str(senders))
    
     
    for i in range(len(contenu_mail)):
        match_str = str(contenu_mail[i])
        match_list = match_str.split("\r\n")
        print("[processing_match] " + match_str)
        if match_list[-1] == '':
            match_list.remove('')
        if len(match_list) == 4:
            player_A, player_A_Score = match_list[0].split(" ")
            player_B, player_B_Score = match_list[1].split(" ")
            player_C, player_C_Score = match_list[2].split(" ")
            player_D, player_D_Score = match_list[3].split(" ")
            
            print("[processing_match] " + "Joueur A:" + player_A)
            print("[processing_match] " + "Joueur B:" + player_B)
            print("[processing_match] " + "Joueur C:" + player_C)
            print("[processing_match] " + "Joueur D:" + player_D)
            print("[processing_match] " + "Joueur A Score:" + player_A_Score)
            print("[processing_match] " + "Joueur B Score:" + player_B_Score)
            print("[processing_match] " + "Joueur C Score:" + player_C_Score)
            print("[processing_match] " + "Joueur D Score:" + player_D_Score)
            if Test_for_Score(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
                if Test_for_TeamScore(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
                    if Test_for_player(player_A, player_B, player_C, player_D):
                
                        
                        player_A = clean_name(player_A)
                        player_B = clean_name(player_B)
                        player_C = clean_name(player_C)
                        player_D = clean_name(player_D)
                        player_A_Elo = get_elo(player_A)
                        player_B_Elo = get_elo(player_B)
                        player_C_Elo = get_elo(player_C)
                        player_D_Elo = get_elo(player_D)  
                        
                        print("[processing_match] " + "Elo Joueur A : " + str(player_A_Elo)) 
                        print("[processing_match] " + "Elo Joueur B : " + str(player_B_Elo))
                        print("[processing_match] " + "Elo Joueur C : " + str(player_C_Elo))
                        print("[processing_match] " + "Elo Joueur D : " + str(player_D_Elo))               
                        Team_1_Elo = team_elo(player_A_Elo, player_B_Elo)
                        Team_2_Elo = team_elo(player_C_Elo, player_D_Elo) 
                        print("[processing_match] " + "Elo Team 1 : " + str(Team_1_Elo))
                        print("[processing_match] " + "Elo Team 2 : " + str(Team_2_Elo))   
                        match(player_A, player_A_Score, Team_1_Elo, Team_2_Elo)
                        match(player_B, player_B_Score, Team_1_Elo, Team_2_Elo)
                        match(player_C, player_C_Score, Team_2_Elo, Team_1_Elo)
                        match(player_D, player_D_Score, Team_2_Elo, Team_1_Elo)
                        print("[processing_match] " + "DONE: " + str(match_list))
                        
                    else:
                        print("[processing_match] " + "Pas 4 joueurs differents ")
                        send_message(service, senders[i], "Elo Rating SMC Program", "Format invalide pour l'email\n" + str(match_list) + '\n\nVeuillez mettre 4 joueurs differents')                  
                else: 
                    send_message(service, senders[i], "Elo Rating SMC Program", "Format invalide pour l'email\n" + str(match_list) + '\n\nVeuillez mettre V en cas de victoire ou D en cas de faite. \nIl ne peut pas y avoir plus de 2 gagnant ni plus de 2 perdant')
                    print("[processing_match] " + "Plus de 2 gagnant ou plus de deux perdant")
            else: 
                send_message(service, senders[i], "Elo Rating SMC Program", "Format invalide pour l'email\n" + str(match_list) + '\n\nVeuillez mettre V en cas de victoire ou D en cas de faite')
                print("[processing_match] " + "Pas de V ou de D")    
        else:     
            
            send_message(service, senders[i], "Elo Rating SMC Program", "Format invalide pour l'email\n" + str(match_list))
            print("[processing_match] " + "Format Invalide")
    print("[processing_match] " + "Done")
