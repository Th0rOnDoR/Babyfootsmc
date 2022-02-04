import os
import datetime
from utils.cte import *


def clean_name(string):
    '''
    Utility fonction that  remove special char from string
    :str string: 
    '''
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

def add_logs(i, text):
    """creating a log file and writting log in it
    :int i: gravity of the log
    :str text: text to add to logs
    """
    print(text)
    today = str(datetime.date.today())
    now = datetime.datetime.now()
    filename = str('logs_' + today + '.txt') 
    while not os.path.isdir('logs'):
        file = os.mkdir("logs")
    filename = str('logs/logs_test_' + today + '.txt') 
    while not os.path.isfile(filename):
        file = open(filename, "w")
        file.close()
    error = ''
    if i == 0:
        error = '[___INFO]   '
    elif i == 1:
        error = '[__WARNING] '
    elif i == 2:
        error = '[_ERROR]    '
    elif i == -1:
        v = default_version()
        error = '[STARTING' + v + ']' 
    else:
        error = '[BLUNDER]   '
        
    
    info = str(error + '[' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + '] ')
    tx = str(info + str(text))
    tx = clean_name(tx)
    tx = tx.split("\n")
    tx = "\n                        ".join(tx)
    tx = tx + '\n'
    file = open(filename, "a")
    file.write(tx)
    file.close()
    return
    
def read_logs(date):
    filename = str('logs/logs_' + date + '.txt') 
    file = open(filename, 'r')
    for lignes in file:
        print(lignes)
    return
