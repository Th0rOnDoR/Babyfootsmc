from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *

import time

def addacc():
    senders = [] #if mail is invalid, sending back an email to warn sender of a blunder so he can send back a correct mail
    contenu_mail = [] #list of str

    results = search_messages(default_addacc_search())  
    for msg in results: #for every mail
        contenu, sender = read_message(msg)
        add_logs(0,str('[processing.addacc] addacc: contenu:' + str(contenu)))
        add_logs(0,str('[processing.addacc] addacc: sender:' + str(sender)))
        sender = sender.split(" ") #to put in to element sender's mail and sender's name 
        if not sender[-1] == 'babyfootsmc@gmail.com': #to remove mail sended by this program
            senders.append(sender[-1])                 #useless now but could be useful
            contenu_mail.append(contenu)
            
    for i in range(len(senders)):
        target = senders[i].split('@')
        target = target[0]
        set_receiver(senders[i], True)
        add_logs(0,str('[processing.addacc] addacc: set receiver true:' + target))
        
    delete_messages(default_addacc_search())
