from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *


def sendmail():
    '''
    for everplayer of classement, send a mail with their score 
    '''
    receiver = get_receiver()
    service = service_gmail()
    classement = get_classement()
    for j in range(len(receiver)):
        for i in range(len(classement)):
            if receiver[j] == classement[i][0]:
                target = receiver[j]
                elo = "\n    Nombres de points ELO: " + str(classement[i][1])
                game = "\n    Nombres de parties: " + str(classement[i][2])
                win = "\n    Nombres de vcitoires: " + str(classement[i][3])
                winstreak = "\n    Nombres de victoire à la suite: " + str(classement[i][4])
                goal = "\n    Nombres de but marqués au total: " + str(classement[i][5])
                
                destination = target + "@smctab.com"
                
                body = "Bonjour,\n\nVoici vos stats dans le classement des joueurs au babyfoot:" + elo + game + win + winstreak + goal + default_end()
                send_message(service, destination, "Elo Rating SMC Program", body)
                add_logs(0,"[processing.send_mail] send_mail: done" + destination)
    add_logs(0,"[processing.send_mail] send_mail: done")
