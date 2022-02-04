import pickle
import os
import re
import io
import requests
import time
from operator import itemgetter
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
#from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *


#excepted(int score_A, int score_B)==================================================
def excepted(A, B):
    return 1/(1+10**((B-A)/400))
#==================================================q


#elo(int previous_elo_A, int previous_elo_B, int state_for_A)=================
def elo(elo_A, elo_B, state_for_A):
    k = 20
    return (k*(state_for_A - excepted(elo_A, elo_B)))
    #==================================================
    
#TEAM_ELO(int JoueurA, int JoueurB)==================================================
def team_elo(Player_A_Elo, Player_B_Elo):   
    team_elo = (1.2*max(Player_A_Elo, Player_B_Elo)+min(Player_A_Elo, Player_B_Elo))/2
    return team_elo
    #==================================================
    
    
#GET_CLASSEMENT==================================================
def get_classement():
    '''
    get a list (of player) of list(of their stat)
    '''
    classement = []
    while not os.path.isdir('data'):
        file = os.mkdir("data")
    while not os.path.isfile('data/stats.py'):
        file = open("data/stats.py", "w")
        file.close()
    fichier = open('data/stats.py', 'r')
    for ligne in fichier:
        if not ligne == "\n":
            classement.append(ligne)
            add_logs(0,str("[utils.elo_utilities] get_classement:" + classement[-1]).replace("\n", ""))
    fichier.close()
    i = 0
    for i in range(len(classement)):
        x = 0
        x = classement[i]
        x = str(x).split(" ")
        y = x[-1] 
        x[-1] = y.split("\n")[0]
        x[1] = int(x[1]) # elo
        x[2] = int(x[2]) # parties
        x[3] = int(x[3]) # victoire
        x[4] = int(x[4]) # winsteak
        x[5] = int(x[5]) # total point marqué
        classement[i] = []
        classement[i] = x 
    return classement
    #==================================================

#GET_ELO(str pseudo)==================================================
def get_elo(target):
    '''
    return elo of a specific player, by iterate over classement list
    '''
    classement = get_classement()
    i = 0
    elo_target = 0
    
    if target == "personne":
        return 0
    if target == "random":
        return 1000
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            elo_target = int(classement[i][1])
            add_logs(0,"[utils.elo_utilities] get_elo: " + target + ": " + str(elo_target) + "Elo")
            return elo_target
    
    fichier = open('data/stats.py', 'a')
    fichier.write(target + ' 1000 0 0 0 0\n')
    add_logs(1,"[utils.elo_utilities] get_elo: " + "[New Player added] " + target)
    set_receiver(target, True)
    fichier.close()
    return 1000
    #==================================================
    
#GET_GAME(str pseudo)==================================================
def get_game(target):
    '''
    return number of game of a specific player, by iterate over classement list
    '''
    classement = get_classement()
    i = 0
    game = 0
    
    if target == "personne":
        return -1
    if target == "random":
        return 0
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            game = int(classement[i][2])
            add_logs(0,"[utils.elo_utilities] get_game: " + target + ": " + str(game) + " games")
            return game
    return 0
    #==================================================
    
    
#GET_WIN(str target)==================================================
def get_win(target):
    '''
    return number of win of a specific player, by iterate over classement list
    '''
    classement = get_classement()
    i = 0
    win = 0
    
    if target == "personne":
        return -1
    elif target == "random":
        return 0
    else:
        for i in range(len(classement)):
            if str(classement[i][0]) == str(target): 
                win = int(classement[i][3])
                add_logs(0,"[utils.elo_utilities] get_win: " + target + ": " + str(win) + " victoires")
                return win
    #==================================================
    
    
#GET_WINSTREAK(str target)==================================================
def get_winstreak(target):
    '''
    return the winstreak of a specific player, by iterate over classement list
    '''
    classement = get_classement()
    i = 0
    winstreak = 0
    
    if target == "personne":
        return -1
    if target == "random":
        return 0
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            winstreak = int(classement[i][4])
            add_logs(0,"[utils.elo_utilities] get_winstreak: " + target + ": " + str(winstreak) + " victoires d'affilee")
            return winstreak
    #==================================================
    
#GET_WINSTREAK(str target)==================================================
def get_goal(target):
    '''
    return the number of goal of a specific player, by iterate over classement list
    '''
    classement = get_classement()
    i = 0
    goal = 0
    
    if target == "personne":
        return -1
    if target == "random":
        return 0
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            goal = int(classement[i][5])
            add_logs(0,"[utils.elo_utilities] get_goal: " + target + ": " + str(goal) + " but")
            return goal
    #==================================================
    

#SET_ELO(str pseudo, int nouvel elo)==================================================
def set_elo(target, elo):
    '''
    change the elo of a specifig target in classement and then re save the stats.py file with ranking
    '''
    if target == "personne":
        return
    if target == "random":
        return
    classement = get_classement()
    i = 0
    classement = sorted(classement, key=itemgetter(0))
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            classement[i][1] = str(str(elo) + "\n")
            fichier = open('data/stats.py', 'w')
            j = 0
            for j in range(len(classement)):
                add_logs(0,"[utils.elo_utilities] set_elo:  " + str(classement[j]))
                fichier.write(str(classement[j][0] + " " + str(int(classement[j][1])) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
            fichier.close()
    return   
    #==================================================
    
#SET_GAME(str pseudo)==================================================
def set_game(target):
    '''
    change the number of game (+1) of a specifig target in classement and then re save the stats.py file with ranking
    '''
    if target == "personne":
        return
    if target == "random":
        return
    classement = get_classement()
    i = 0
    game = get_game(target)
    game += 1
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            classement[i][2] = str(game)
            fichier = open('data/stats.py', 'w')
            j = 0
            for j in range(len(classement)):
                add_logs(0,"[utils.elo_utilities] set_game: " + str(classement[j]))
                fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
            fichier.close()
    return   
    #==================================================

#SET_WIN(str pseudo, int score)==================================================
def set_win(target, score):
    '''
    change the number of win of a specifig target in classement and then re save the stats.py file with ranking
    '''
    if target == "personne":
        return
    if target == "random":
        return
    classement = get_classement()
    i = 0
    if score == 0:
        return 
    if score == 1:
        win = get_win(target) + 1
        for i in range(len(classement)):
            if str(classement[i][0]) == str(target): 
                classement[i][3] = str(win)
                fichier = open('data/stats.py', 'w')
                j = 0
                for j in range(len(classement)):
                    add_logs(0,"[utils.elo_utilities] set_win: " + str(classement[j]))
                    fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
                fichier.close()
    return   
    #==================================================
    
#SET_WINSTREAK(str pseudo, int score)==================================================
def set_winstreak(target, score):
    '''
    change the winstreak of a specifig target in classement and then re save the stats.py file with ranking
    '''
    if target == "personne":
        return
    if target == "random":
        return
    classement = get_classement()
    i = 0
    winstreak = get_winstreak(target)
    if score == 0:
        #if he loose
        if winstreak <= 0:
            #if he was previously loosing, adding another loose
            fichier = open('data/stats.py', 'w')
            fichier.close()
            j = 0
            winstreak += -1
            for i in range(len(classement)):
                if str(classement[i][0]) == str(target): 
                    classement[i][4] = str(winstreak)
                    for j in range(len(classement)):
                        fichier = open('data/stats.py', 'a')
                        add_logs(0,"[utils.elo_utilities] set_winstreak: " + str(classement[j]))
                        
                        fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
                        fichier.close()
        if winstreak > 0:
            #if he was winning, reset winstreak
            j = 0
            winstreak = 0
            fichier = open('data/stats.py', 'w')
            for i in range(len(classement)):
                if str(classement[i][0]) == str(target): 
                    classement[i][4] = str(winstreak)
                    for j in range(len(classement)):
                        add_logs(0,"[utils.elo_utilities] set_winstreak: " + str(classement[j]))
                        fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
            fichier.close()
    if score == 1:
        #if he won
        if winstreak < 0:
            #if he was loosing, reset
            j = 0
            fichier = open('data/stats.py', 'w')
            winstreak = 0
            for i in range(len(classement)):
                if str(classement[i][0]) == str(target): 
                    classement[i][4] = str(winstreak)
                    for j in range(len(classement)):
                        add_logs(0,"[utils.elo_utilities] set_winstreak: " + str(classement[j]))
                        fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
            fichier.close()
        if winstreak >= 0:
            #if he was winning, add another win
            j = 0
            fichier = open('data/stats.py', 'w')
            winstreak = winstreak + 1
            for i in range(len(classement)):
                if str(classement[i][0]) == str(target): 
                    classement[i][4] = str(winstreak)
                    for j in range(len(classement)):
                        add_logs(0,"[utils.elo_utilities] set_winstreak: " + str(classement[j]))
                        fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
            fichier.close()
            
    
    return   
    #==================================================
    
#SET_GOAL(str pseudo, int goal)==================================================
def set_goal(target, score):
    '''
    change the number of goal of a specifig target in classement and then re save the stats.py file with ranking
    '''
    if target == "personne":
        return
    if target == "random":
        return
    classement = get_classement()
    i = 0
    goal = get_goal(target) + score
    for i in range(len(classement)):
        if str(classement[i][0]) == str(target): 
            classement[i][5] = str(goal)
            fichier = open('data/stats.py', 'w')
            j = 0
            for j in range(len(classement)):     
                add_logs(0,"[utils.elo_utilities] set_goal: " + str(classement[j]))
                fichier.write(str(classement[j][0] + " " + str(classement[j][1]) + " " + str(classement[j][2]) + " " + str(classement[j][3]) + " " + str(classement[j][4]) + " " + str(classement[j][5]) + "\n"))
            fichier.close()
    return   
    #==================================================
    
    # + total point marque
    
    
#GET_DELTA_ELO(str player)==================================================   
def get_delta_elo(target):
    '''
    get the delta elo of a specifig target in cache file like done with get_classement()
    '''
    if target == "personne":
        return 0
    if target == "random":
        return 0
    delta_elo = []
    while not os.path.isfile('data/cache.py'):
        file = open("data/cache.py", "w")
        file.close()  
    file = open('data/cache.py', 'r')
    for ligne in file:
        if not ligne == "\n":
            delta_elo.append(ligne)
            add_logs(0,"[utils.elo_utilities] get_delta_elo: " + delta_elo[-1].replace('\n', ''))
    file.close()
    i = 0
    for i in range(len(delta_elo)):
        x = ''
        x = delta_elo[i]
        x = str(x).split(" ")
        y = x[-1] 
        x[-1] = y.split("\n")[0]
        x[1] = int(x[1]) # elo
        delta_elo[i] = []
        delta_elo[i] = x 
    for j in range(len(delta_elo)):
        if str(delta_elo[j][0]) == str(target): 
            delta_elo_target = int(delta_elo[j][1])
            add_logs(0,"[utils.elo_utilities] get_delta_elo: " + target + ": " + str(delta_elo_target) + "Elo")
            return delta_elo_target, delta_elo
    fichier = open("data/cache.py","a")
    fichier.write(str(target) + " " + "0\n")
    fichier.close()
    return 0, delta_elo
    #==================================================
    
#SET_DELTA_ELO(str player, int elo win)==================================================
def set_delta_elo(target, elo):
    '''
    change the delta_elo of a specifig target in delta_elo list and then re save the cache.py file with update war
    '''
    if target == "personne":
        return 0
    if target == "random":
        return 0
    delta_elo_target, delta_elo = get_delta_elo(target)
    delta_elo_target = elo + delta_elo_target
    if delta_elo_target > 50:
        return 0
    if delta_elo_target < -50:
        return 0
    if delta_elo_target < 50:
        i = 0
        for i in range(len(delta_elo)):
            if str(delta_elo[i][0]) == str(target): 
                delta_elo[i][1] = str(str(delta_elo_target) + "\n")
                fichier = open('data/cache.py', 'w')
                j = 0
                for j in range(len(delta_elo)):
                    delta_elo[j][1] = str(delta_elo[j][1])
                    add_logs(0,"[utils.elo_utilities] delta_elo: " + str(delta_elo[j]))
                    fichier.write(str(delta_elo[j][0]) + " " + str(delta_elo[j][1]) + "\n")
                fichier.close()
        return elo
    #==================================================

