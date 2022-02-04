
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
#from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *

#MATCH(str joueur, int issue[0 ou 1], int Elo_Team_Joueur, int Elo_Team_Adversaire, int goal========
def match(Player, player_Score, Team_1, Team_2, perdant):
    '''
    update every stats and delta_elo of a player
    :str Player: the main player
    :str player_Score: the score of the player depending of mail
    :int Team_1: elo rating of team 1 (player's team)
    :int Team_2: elo rating of team 2 (the other one)
    '''
    player_Elo = get_elo(Player)
    if player_Score == "V":
        player_Score = 1
        
    elif player_Score == "D":
        player_Score = 0
    elo_add = 0
    elo_add = int(elo(Team_1, Team_2, player_Score))
    
    if player_Score == 1:
        delta_elo = set_delta_elo(Player, elo_add) 
        delta_elo = delta_elo + (10-perdant) #adding score difference
        print(type(delta_elo))
        if delta_elo != 0:
            elo + delta_elo
    if player_Score == 0:
        player_Elo += set_delta_elo(Player, elo_add) #adding score difference
    set_elo(Player, player_Elo)
    add_logs(0,'[utils.match_utilities] match: elo done for ' + Player)
    set_game(Player)
    add_logs(0,'[utils.match_utilities] match: game done for ' + Player)
    set_win(Player, player_Score)
    add_logs(0,'[utils.match_utilities] match: win done for ' + Player) 
    set_winstreak(Player, player_Score)
    add_logs(0,'[utils.match_utilities] match: winstreak done for ' + Player)
    return
    #==================================================



#==================================================
def clean_name(string):
    '''
    Utility fonction that  remove special char from string
    :str string: 
    '''
    add_logs(0,'[utils.match_utilities] clean_name: cleaning: ' + string) 
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
    add_logs(0,'[utils.match_utilities] clean_name: cleaned: ' + string) 
    return string
    #==================================================
#==================================================
def Test_for_Score(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
    '''
    Test to see if someone try to cheat on a match or done a missclick
    '''
    
    A = (player_A_Score == 'V' or player_A_Score == 'D')
    B = (player_B_Score == 'V' or player_B_Score == 'D')
    C = (player_C_Score == 'V' or player_C_Score == 'D')
    D = (player_D_Score == 'V' or player_D_Score == 'D')
    add_logs(0,"[utils.match_utilities] Test_For_TeamScore: A = " + str(A) + " B = " + str(B) + " C = " + str(C)  + " D = " + str(D))
    
    if A and B and C and D:
        return True
    else:
        return False 
    #==================================================

#==================================================
def Test_for_TeamScore(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
    '''
    Test to see if someone try to cheat on a match or done a missclick
    '''
    A = player_A_Score == player_B_Score 
    B = player_C_Score == player_D_Score 
    C = player_A_Score != player_D_Score
    add_logs(0,"[utils.match_utilities] Test_For_TeamScore: A = " + str(A) + " B = " + str(B) + " C = " + str(C))
    if A and B and C:
        return True
    else:
        return False 
    #==================================================

#==================================================
def Test_for_player(player_A, player_B, player_C, player_D):
    '''
    Test to see if someone try to cheat on a match or done a missclick
    '''
    if player_A == "personne" or player_B == "personne" or player_C == "personne" or player_D == "personne":
        A = player_A != player_B or player_A == "personne" or player_B == "personne"
        B = player_C != player_D or player_C == "personne" or player_D == "personne"
        C = player_A != player_D or player_A == "personne" or player_D == "personne"
        D = player_B != player_C or player_B == "personne" or player_C == "personne"
        
        add_logs(0,"[utils.match_utilities] Test_For_Player: A = " + str(A) + " B = " + str(B) + " C = " + str(C) + " D = " + str(D))
    
    else:
        A = player_A != player_B
        B = player_C != player_D
        C = player_A != player_D
        D = player_B != player_C
        
        add_logs(0,"[utils.match_utilities] Test_For_Player: A = " + str(A) + " B = " + str(B) + " C = " + str(C) + " D = " + str(D))
    if A and B and C and D:
        return True
    else: 
        return False
    #==================================================
    

#==================================================

