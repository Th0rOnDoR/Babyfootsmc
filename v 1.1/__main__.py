
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
    """
    the main fonction
    """
    
    #show menu
    print("Traitement matchs: match")
    print("Suppresion email: mail (del/send/customsend/check)")
    print("Mise a jour des comptes: acc (del/add)")
    print("Mise à jour du drive: drive (elo/backup)")
    
    #input cmd
    cmd = input("Cmd ?")
    cmd = cmd.split(" ")
    
    #if too much args
    if len(cmd) != 1:
        return
        
        
    #first command, show rating of everyplayer
    if cmd[0] == "c":
        print(tabulate(sorted(get_classement(), key=itemgetter(1)), headers=["Joueur", "Points ", "Parties", "Victoire", "Winstreak", "Total goal"]))
    
    #process match, see do_match.py
    if cmd[0] == "match":
        #to process match only
        add_logs(-1,"[main] match:")
        do_match()
        
    #edit list of player who wants to receive mail
    if cmd[0] == "acc":
        
        #input subcommand
        cmd.append(input('add / del'))

        #remove someone from list
        if cmd[1] == "del":
            add_logs(-1,"[main] delacc:")
            delacc()
        
        #add someone
        elif cmd[1] == "add":
            add_logs(-1,"[main] addacc:")
            addacc()

    #mail
    if cmd[0] == "mail":
        #sub command
        cmd.append(input('del / send / customsend(tx,d) / check'))
        #del mail with results
        if cmd[1] == "del":
            add_logs(-1,"[main] delmail:")
            delmail()
            
        #send default mail with stats to everyone in receiver.py
        if cmd[1] ==  "send":
            add_logs(-1,"[main] sendmail:")
            sendmail()
        
        #send a custom mail to everyone
        if cmd[1] == "customsend":
            t = input('text to send')
            d = input('to who (all, actif, someone)')
            add_logs(-1,"[main] send_custom_mail:")
            sendcustom_mail(t, d)
        
        #check if there is something to see in mailbox
        if cmd[1] == ("check"):
            add_logs(-1,"[main] mailerror:")
            mailerror()
        
    #drive
    if cmd[0] == "drive":
        cmd.append(input('elo / backup'))
        
        #update elp
        if cmd[1] == "elo":
            add_logs(-1,"[main] elo_update:")
            elo_update()
            
        #add a new backup
        if cmd[1] == "backup":
            add_logs(-1,"[main] backup:")
            backup()

    #default command, do everything
    if cmd[0] == "":
        #first, match
        add_logs(-1,"[main] main:")
        do_match()
        
        i = 0 #timer 
        for i in range(0,10):
            print("waiting until 10: " + str(i))
            time.sleep(1)
        
        
        
        addacc()
        
        
        time.sleep(1)
        
        
        elo_update()
        
        
        time.sleep(1)
        
        
        delacc()
        
        for i in range(0,5):
            print("waiting until 5: " + str(i))
            time.sleep(1)
            
            
        sendmail()
        
        
        for i in range(0,5):
            print("waiting until 5: " + str(i))
            time.sleep(1)
            
            
        backup()
        
        
        for i in range(0,5):
            print("waiting until 5: " + str(i))
            time.sleep(1)
            
            
        delmail()
        
        
        time.sleep(1)
        
        
        os.remove('data/cache.py')
        
        
        time.sleep(1)
        
        
        mailerror()
        
        
        print("\n\n\nEND")
    
    


if __name__ == "__main__":
    main()
    

