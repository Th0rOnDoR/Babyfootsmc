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
#from utils.elo_utilities import *
from utils.drive import *
#from processing_match import *
#from processing_delmail import *
#from processing_drive import *


#excepted(int score_A, int score_B)==================================================
def excepted(A, B):
    return 1/(1+10**((B-A)/400))
#==================================================q


#elo(int previous_elo_A, int previous_elo_B, int state_for_A)=================
def elo(elo_A, elo_B, state_for_A):
    k = 40
    return (k*(state_for_A - excepted(elo_A, elo_B)))
    #==================================================
    
#GET_CLASSEMENT==================================================
def get_classement():
    classement = []
    fichier = open('elo.py', 'r')
    for ligne in fichier:
        if not ligne == "\n":
            classement.append(ligne)
            print("[elo_utilities] " + classement[-1])
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

#GET_ELO(str pseudo)==================================================
def get_elo(target):
    classement = get_classement()
    i = 0
    elo_target = 0
    
    if target == "personne":
        return 0
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            elo_target = int(classement[i][1])
            print("[elo_utilities] " + target + ": " + str(elo_target) + "Elo")
            return elo_target
    
    fichier = open('elo.py', 'a')
    fichier.write(target + ' 1000\n')
    print("[elo_utilities] " + "[New Player added] " + target)
    fichier.close()
    return 1000
    #==================================================


#SET_ELO(str pseudo, int nouvel elo)==================================================
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
                print("[elo_utilities] " + str(classement[j]))
                classement_save = " ".join(classement[j])
                fichier.write(str(classement[j][0] + " " + str(classement[j][1]) +"\n"))
            fichier.close()
    return   
    #==================================================

#MATCH(str joueur, int issue[0 ou 1], int Elo_Team_Joueur, int Elo_Team_Adversaire =======================
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


#TEAM_ELO(int JoueurA, int JoueurB)==================================================
def team_elo(Player_A_Elo, Player_B_Elo):   
    team_elo = (1.2*max(Player_A_Elo, Player_B_Elo)+min(Player_A_Elo, Player_B_Elo))/2
    return team_elo
    #==================================================
    
#==================================================
def clean_name(string):
    string = string.replace("â", "a")
    string = string.replace("æ", "ae")
    string = string.replace("à", "a")
    string = string.replace("ê", "e")
    string = string.replace("é", "e")
    string = string.replace("è", "e")
    string = string.replace("ë", "e")
    string = string.replace("î", "i")
    string = string.replace("ï", "i")
    string = string.replace("ì", "i")
    string = string.replace("í", "i")
    string = string.replace("ö", "o")
    string = string.replace("ó", "o")
    string = string.replace("ô", "o")
    string = string.replace("œ", "oe")
    string = string.replace("ò", "o")
    string = string.replace("ü", "u")
    string = string.replace("û", "u")
    string = string.replace("ù", "u")
    string = string.replace("ú", "u")
    string = string.replace("ÿ", "y")
    return string
    #==================================================
#==================================================
def Test_for_Score(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
    
    A = (player_A_Score == 'V' or player_A_Score == 'D')
    B = (player_B_Score == 'V' or player_B_Score == 'D')
    C = (player_C_Score == 'V' or player_C_Score == 'D')
    D = (player_D_Score == 'V' or player_D_Score == 'D')
    
    if A and B and C and D:
        return True
    else:
        return False 
    #==================================================

#==================================================
def Test_for_TeamScore(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
    A = player_A_Score == player_B_Score 
    B = player_C_Score == player_D_Score 
    C = player_A_Score != player_D_Score
    if A and B and C:
        return True
    else:
        return False 
    #==================================================

#==================================================
def Test_for_player(player_A, player_B, player_C, player_D):
    if player_A == "personne" or player_B == "personne" or player_C == "personne" or player_D == "personne":
        A = player_A != player_B or player_A == "personne" or player_B == "personne"
        B = player_C != player_D or player_C == "personne" or player_D == "personne"
        C = player_A != player_D or player_A == "personne" or player_D == "personne"
        D = player_B != player_C or player_B == "personne" or player_C == "personne"
        
        print("[elo_utilities] A = " + str(A) + " B = " + str(B) + " C = " + str(C) + " D = " + str(D))
    
    else:
        A = player_A != player_B
        B = player_C != player_D
        C = player_A != player_D
        D = player_B != player_C
        
        print("[elo_utilities] A = " + str(A) + " B = " + str(B) + " C = " + str(C) + " D = " + str(D))
    if A and B and C and D:
        return True
    else: 
        return False
    #==================================================


