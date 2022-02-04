from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *


def sendcustom_mail(text, destination):
    """
    send custom mail to a list of player, all or just someone 
    """
    service = service_gmail()
    body = text + default_end()
    if destination == "all":
        classement = get_classement()
        for i in range(len(classement)):
            destination = str(classement[i][0]) + '@smctab.com'
            send_message(service, destination, "SMC babyfoot ranking program", body)
            add_logs(0,"[processing.sendcustom_mail] sendcustom_mail: done" + destination)
        add_logs(0,"[processing.sendcustom_mail] sendcustom_mail: done")
    elif destination == "actif":
        receiver = get_receiver()
        for i in range(len(receiver)):
            destination = str(receiver[i]) + '@smctab.com'
            send_message(service, destination, "SMC babyfoot ranking program", body)
            add_logs(0,"[processing.sendcustom_mail] sendcustom_mail: done" + destination)
        add_logs(0,"[processing.sendcustom_mail] sendcustom_mail: done")
    else:
        send_message(service, destination, "SMC babyfoot ranking program", body)
        add_logs(0,"[processing.sendcustom_mail] sendcustom_mail: done")
        
