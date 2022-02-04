
import time
from operator import itemgetter

from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *
from processing.do_match import *
from processing.backup import *
from processing.delmail import *
from processing.sendmail import *
from processing.sendcustom_mail import *
from processing.elo_update import *
from processing.delacc import *
from processing.addacc import *
from processing.mailerror import *

def main():

    print("Traitement matchs: match")
    print("Suppresion email: mail (del/send/customsend/check)")
    print("Mise a jour des comptes: acc (del/add)")
    print("Mise à jour du drive: drive (elo/backup)")
    cmd = input("Cmd ?")
    cmd = cmd.split(" ")
    if len(cmd) != 2 and len(cmd) != 1:
        #if too much args
        return
    if cmd[0] == "c":
        print(tabulate(sorted(get_classement(), key=itemgetter(1)), headers=["Joueur", "Points ", "Parties", "Victoire", "Winstreak", "Total goal"]))
    if cmd[0] == "match":
        #to process match only
        add_logs(-1,"[main] match:")
        do_match()
    if cmd[0] == "acc":
        if cmd[1] == "del":
            add_logs(-1,"[main] delacc:")
            delacc()
        if cmd[1] == "add":
            add_logs(-1,"[main] addacc:")
            addacc()

    if cmd[0] == "mail":
        if cmd[1] == "del":
            add_logs(-1,"[main] delmail:")
            delmail()
        if cmd[1] ==  "send":
            add_logs(-1,"[main] sendmail:")
            sendmail()
        if cmd[1] == "customsend":
            t = input('text to send')
            d = input('to who')
            add_logs(-1,"[main] send_custom_mail:")
            sendcustom_mail(t, d)
        if cmd[1] == ("check"):
            add_logs(-1,"[main] mailerror:")
            mailerror()
        
    if cmd[0] == "drive":
        if cmd[1] == "elo":
            add_logs(-1,"[main] elo_update:")
            elo_update()
        if cmd[1] == "backup":
            add_logs(-1,"[main] backup:")
            backup()

    if cmd[0] == "":
        
        add_logs(-1,"[main] main:")
        do_match()
        
        i = 0
        for i in range(0,20):
            print("waiting until 20: " + str(i))
            time.sleep(1)
            
        addacc()
        
        delacc()
        
        backup()
        for i in range(0,5):
            print("waiting until 5: " + str(i))
            time.sleep(1)
            
        
        elo_update()
        
        i = 0
        for i in range(0,5):
            print("waiting until 5: " + str(i))
            time.sleep(1)
            
        sendmail()
        
        i = 0
        for i in range(0,5):
            print("waiting until 5: " + str(i))
            time.sleep(1)
            
        delmail()
        while os.path.isfile('data/cache.py'):
            os.remove('data/cache.py')
        mailerror()
        print("\n\n\nFIN")
    
    


if __name__ == "__main__":
    main()
    
'''
print(tabulate(get_classement(), headers=["Joueur", "Points ", "Parties", "Victoire", "Winstreak", "Total goal"]))
'''
