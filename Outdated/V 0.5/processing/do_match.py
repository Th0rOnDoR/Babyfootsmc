from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *

def do_match():
    '''
    opening every mail with subjet CLASSEMENT and then reading them to update every stats and ranking of each player
    '''
    senders = [] #if mail is invalid, sending back an email to warn sender of a blunder so he can send back a correct mail
    contenu_mail = [] #list of an st

    results = search_messages("Subject:CLASSEMENT in:inbox")  
    for msg in results: #for every mail
        contenu, sender = read_message(msg)
        sender = sender.split(" ") #to put in to element sender's mail and sender's name 
        if not sender[-1] == 'babyfootsmc@gmail.com': #to remove mail sended by this program
            senders.append(sender[-1])                 #useless now but could be useful
            contenu_mail.append(contenu)
            
    contenu_mail.reverse()
    senders.reverse()
    i = 0 
    classement = []
    print("[processing.match] do_match: senders:" + str(senders))
    
     
    for i in range(len(contenu_mail)): #begin of mail procesz
        good_format = True
        match_str = str(contenu_mail[i]) #extract element i into an str and then into a list
        match_list = match_str.split("\r\n")
        print("[processing.match] do_match: good_format: " + str(good_format))
        print("[processing.match] do_match: match_str: " + match_str)
        print("[processing.match] do_match: match_list" + str(match_list)) #list of every line in mail
        if match_list[-1] == '':
            match_list.remove('') #if any blank line
        if len(match_list) == 5: #see doc to understand why
            for k in range(len(match_list)):
                print("[processing.match] do_match: match_list_i:" + match_list[k])
                match_list[k] = match_list[k].split(" ")
                if k < 4: #the last element should be only 1 item so...
                    if len(match_list[k]) != 2:
                        good_format = False
            #i prefer use a lot of war than one list of list x), it's easier to understand 
            try:      
                player_A = match_list[0][0].lower()
                player_B = match_list[1][0].lower()
                player_C = match_list[2][0].lower()
                player_D = match_list[3][0].lower()
                player_A_Score = match_list[0][1].upper()
                player_B_Score = match_list[1][1].upper()
                player_C_Score = match_list[2][1].upper()
                player_D_Score = match_list[3][1].upper()
                perdant = int(match_list[4][0])
            
                print("[processing.match] do_match: " + "Joueur A:" + player_A)
                print("[processing.match] do_match: " + "Joueur B:" + player_B)
                print("[processing.match] do_match: " + "Joueur C:" + player_C)
                print("[processing.match] do_match: " + "Joueur D:" + player_D)
                print("[processing.match] do_match: " + "Joueur A Score:" + player_A_Score)
                print("[processing.match] do_match: " + "Joueur B Score:" + player_B_Score)
                print("[processing.match] do_match: " + "Joueur C Score:" + player_C_Score)
                print("[processing.match] do_match: " + "Joueur D Score:" + player_D_Score)
                print("[processing.match] do_match: " + "Score perdant:" + str(perdant))
            except IndexError:
                good_format = False
            
            if good_format:
                if Test_for_Score(player_A_Score, player_B_Score, player_C_Score, player_D_Score) and good_format:
                    #if more than to D or two V
                    if Test_for_TeamScore(player_A_Score, player_B_Score, player_C_Score, player_D_Score):
                        #if teammate doesnt have the same score
                        if Test_for_player(player_A, player_B, player_C, player_D):
                            #if player are the same 
                            if perdant >= -10 and perdant <10:
                                #someone tried to put -1000 to win 1000 elo so...
                                #doesnt care to know if someone of the team goal 7times and the other 1, 
                                #they're a team so it's team work
                                
                                
                                if player_A_Score == 'D' and player_B != "personne":
                                    player_A_goal = int(perdant/2)
                                elif player_A_Score == 'D' and player_B == "personne": 
                                    player_A_goal = perdant
                                elif player_A_Score == 'V' and player_B != "personne":
                                    player_A_goal = 10
                                elif player_A_Score == 'D' and player_B == "random": 
                                    player_A_goal = perdant/2
                                elif player_A_Score == 'V' and player_B != "random":
                                    player_A_goal = 5
                                else: 
                                    player_A_goal = 10
                                
                                
                                if player_B_Score == 'D' and player_A != "personne":
                                    player_B_goal = int(perdant/2)
                                elif player_B_Score == 'D' and player_A == "personne":
                                    player_B_goal = perdant
                                elif player_B_Score == 'V' and player_A != "personne":
                                    player_B_goal = 10
                                elif player_B_Score == 'D' and player_A == "random": 
                                    player_B_goal = perdant/2
                                elif player_B_Score == 'V' and player_A != "random":
                                    player_B_goal = 5
                                else: 
                                    player_B_goal = 10
                                
                                if player_C_Score == 'D' and player_D != "personne":
                                    player_C_goal = int(perdant/2)
                                elif player_C_Score == 'D' and player_D == "personne":
                                    player_C_goal = perdant
                                elif player_C_Score == 'D' and player_D == "random": 
                                    player_C_goal = perdant/2
                                elif player_C_Score == 'V' and player_D != "random":
                                    player_C_goal = 5
                                elif player_C_Score == 'V' and player_D != "personne":
                                    player_C_goal = 10
                                else: 
                                    player_C_goal = 10
                                 
                                       
                                if player_D_Score == 'D' and player_C != "personne":
                                    player_D_goal = int(perdant/2)
                                elif player_D_Score == 'D' and player_C == "personne":
                                    player_D_goal = perdant
                                elif player_D_Score == 'D' and player_C == "random": 
                                    player_D_goal = perdant/2
                                elif player_D_Score == 'V' and player_C != "random":
                                    player_D_goal = 5
                                elif player_D_Score == 'V' and player_C != "personne":
                                    player_D_goal = 10
                                else: 
                                    player_D_goal = 10
                                
                    
                                player_A = clean_name(player_A) #to remove à and ë and î, this 
                                player_B = clean_name(player_B) #kind of things
                                player_C = clean_name(player_C)
                                player_D = clean_name(player_D)
                                player_A_Elo = get_elo(player_A)
                                player_B_Elo = get_elo(player_B)
                                player_C_Elo = get_elo(player_C)
                                player_D_Elo = get_elo(player_D)  
                                
                                print("[processing.match] do_match: " + "Elo Joueur A : " + str(player_A_Elo)) 
                                print("[processing.match] do_match: " + "Elo Joueur B : " + str(player_B_Elo))
                                print("[processing.match] do_match: " + "Elo Joueur C : " + str(player_C_Elo))
                                print("[processing.match] do_match: " + "Elo Joueur D : " + str(player_D_Elo))               
                                Team_1_Elo = team_elo(player_A_Elo, player_B_Elo) #calculing team elo
                                Team_2_Elo = team_elo(player_C_Elo, player_D_Elo) #for each team
                                print("[processing.match] do_match: " + "Elo Team 1 : " + str(Team_1_Elo))
                                print("[processing.match] do_match: " + "Elo Team 2 : " + str(Team_2_Elo))   
                                match(player_A, player_A_Score, Team_1_Elo, Team_2_Elo, perdant)
                                match(player_B, player_B_Score, Team_1_Elo, Team_2_Elo, perdant)
                                match(player_C, player_C_Score, Team_2_Elo, Team_1_Elo, perdant)
                                match(player_D, player_D_Score, Team_2_Elo, Team_1_Elo, perdant)
                                set_goal(player_A, player_A_goal)
                                set_goal(player_B, player_B_goal)
                                set_goal(player_C, player_C_goal)
                                set_goal(player_D, player_D_goal)
                                #match contains code that was previously here but took to much place for 
                                #something repeat 4 times like that
                                print("[processing.match] do_match: " + "DONE: " + str(match_list))
                            else:
                                send_message(senders[i], "SMC babyfoot ranking program", "Format invalide pour l'email\n" + str(match_list) + '\n\nScore incorrect ou impossible')
                                print("[processing.match] do_match: score incorrect")
                        else:
                            print("[processing.match] do_match: " + "Pas 4 joueurs differents ")
                            send_message(senders[i], "SMC babyfoot ranking program", "Format invalide pour l'email\n" + str(match_list) + '\n\nVeuillez mettre 4 joueurs differents')                  
                    else: 
                        send_message(senders[i], "SMC babyfoot ranking program", "Format invalide pour l'email\n" + str(match_list) + '\n\nVeuillez mettre V en cas de victoire ou D en cas de faite. \nIl ne peut pas y avoir plus de 2 gagnant ni plus de 2 perdant')
                        print("[processing.match] do_match: " + "Plus de 2 gagnant ou plus de deux perdant")
                else: 
                    send_message(senders[i], "SMC babyfoot ranking program", "Format invalide pour l'email\n" + str(match_list) + '\n\nVeuillez mettre V en cas de victoire ou D en cas de faite')
                    print("[processing.match] do_match: " + "Pas de V ou de D")    
            else:            
                send_message(senders[i], "SMC babyfoot ranking program", "Format invalide pour l'email\n" + str(match_list))
                print("[processing.match] do_match: " + "Format Invalide")
        else:            
            send_message(senders[i], "SMC babyfoot ranking program", "Format invalide pour l'email\n" + str(match_list))
            print("[processing.match] do_match: " + "Format Invalide")
    print("[processing_match] " + "Done")
