from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *


def sendcustom_mail(text, destination):
    '''
    send custom mail to a list of player, all or just someone 
    '''
    body = text + default_end()
    if destination == "all":
        classement = get_classement()
        for i in range(len(classement)):
            destination = str(classement[i][0]) + '@smctab.com'
            send_message(destination, "SMC babyfoot ranking program", body)
            print("[processing.sendcustom_mail] sendcustom_mail: done" + destination)
        print("[processing.sendcustom_mail] sendcustom_mail: done")
    else:
        send_message(destination, "SMC babyfoot ranking program", body)
        print("[processing.sendcustom_mail] sendcustom_mail: done")
        
