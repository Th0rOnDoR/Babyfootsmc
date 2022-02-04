from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *


def sendmail():
    '''
    for everplayer of classement, send a mail with their score 
    '''
    classement = get_classement()
    for i in range(len(classement)):
        target = classement[i][0]
        elo = "\n    Nombres de points ELO: " + str(get_elo(target))
        game = "\n    Nombres de parties: " + str(get_game(target))
        win = "\n    Nombres de vcitoires: " + str(get_win(target))
        winstreak = "\n    Nombres de victoire à la suite: " + str(get_winstreak(target))
        goal = "\n    Nombres de but marqués au total: " + str(get_goal(target))
        
        destination = target + "@smctab.com"
        
        body = "Bonjour,\n\nVoici vos stats dans le classement des joueurs au babyfoot:" + elo + game + win + winstreak + goal + default_end()
        send_message(destination, "Elo Rating SMC Program", body)
        print("[processing.send_mail] send_mail: done" + destination)
    print("[processing.send_mail] send_mail: done")
