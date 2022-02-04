
import time

from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from processing.match import *
from processing.backup import *
from processing.delmail import *
from processing.sendmail import *
from processing.sendcustom_mail import *
from processing.elo_update import *

def main():

    print("Traitement matchs: match")
    print("Suppresion email: mail (del/send/customsend)")
    print("Mise à jour du drive: drive (elo/backup)")
    cmd = input("Cmd ?")
    cmd = cmd.split(" ")
    if len(cmd) != 2 and len(cmd) != 1:
        #if too much args
        return
    if cmd[0] == "match":
        #to process match only
        do_match()
        

    if cmd[0] == "mail":
        if cmd[1] == "del":
            delmail()
        if cmd[1] ==  "send":
            sendmail()
        if cmd[1] == "customsend":
            t = input('text to send')
            d = input('to who')
            sendcustom_mail(t, d)
    if cmd[0] == "drive":
        if cmd[1] == "elo":
            elo_update()
        if cmd[1] == "backup":
            backup()

    if cmd[0] == "":
        do_match()
        i = 0
        for i in range(0,20):
            print("waiting until 20: " + str(i))
            time.sleep(1)
        elo_update()
        for i in range(0,10):
            print("waiting until 10: " + str(i))
            time.sleep(1)
        sendmail()
        i = 0
        for i in range(0,10):
            print("waiting until 10: " + str(i))
            time.sleep(1)
        backup()
        i = 0
        for i in range(0,10):
            print("waiting until 10: " + str(i))
            time.sleep(1)
        delmail()
        os.remove('cache.py')
        print("\n\n\nFIN")
    
    


if __name__ == "__main__":
    main()
