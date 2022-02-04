from datetime import date
from operator import itemgetter
from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *


def elo_update():
    '''
    creating a file of ranking then uploading it into main folder 
    for each player, creating a file and then uploading it into the folder of the player to see player's rating evolution
    '''
    service = get_gdrive_service() #getting drive service
    main_folder = id_main_folder() #not root folder on drive but the sharing folder
    score_folder= id_score_folder() #score folder to put every player stats
    classement_folder = id_classement_folder() #folder to put classement general in
    today = str(date.today()) # to name the file
    add_logs(0,"[processing.elo_update] elo_update: today: " + today) 
    
    
    
    classement = get_classement()
    filename = "classement general " + today + ".txt"
    add_logs(0,"[processing.elo_update] elo_update: filename: " + filename)   
    file = open(filename, "w") 
    file.write(tabulate(sorted(classement, key=itemgetter(1)), headers=["Joueur", "Points ", "Parties", "Victoire", "Winstreak", "Total goal"]))
    file.close()
    upload_files(filename, classement_folder) #uploading file then we'll delete it
    add_logs(0,"[processing.elo_update] elo_update: uploaded:" + filename + "  in: " + classement_folder)
    
    if os.path.exists(filename): #delete if exist
        os.remove(filename)
        add_logs(0,"[processing.elo_update] elo_update: deleting cache file " + filename)
    else: #else, no need, it doesnt exist
        add_logs(0,"[processing.elo_update] elo_update: The file does not exist") 
    
    
    
    
    i = 0
    for i in range(len(classement)):
        folder_id = search_for_folder(classement[i][0])
        #searching for folder of every player
        
        if folder_id == "false": #if doesnt exist create one in score's folder
            folder_metadata = {
                "name": classement[i][0],
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [score_folder]
            }
            folder = service.files().create(body=folder_metadata, fields="id").execute()
            folder_id = folder.get("id") #get if of folder we just create
            filename = str(today + ".txt") 
            add_logs(0,"[processing.elo_update] elo_update: creating cache file " + filename)
            file = open(filename, "w")
            classement[i][1] = str(classement[i][1])
            classement[i][2] = str(classement[i][2])
            classement[i][3] = str(classement[i][3])
            classement[i][4] = str(classement[i][4])
            classement[i][5] = str(classement[i][5])
            file.write(" ".join(classement[i]) + "\n") #create a file with only one line witb player's stats
            file.close()
            upload_files(filename, folder_id)
            add_logs(0,"[processing.elo_update] elo_update: uploaded:" + filename + "  in: " + folder_id)
                
            if os.path.exists(filename): # deleting file as previous 
                os.remove(filename)
                add_logs(0,"[processing.elo_update] elo_update: deleting cache file " + filename)
            else:
                add_logs(1,"[processing.elo_update] elo_update: The file does not exist")
        else: #if a folder already exist (even in trash, this was really boring)
            filename = str(classement[i][0] + " " + today + ".txt")
            file = open(filename, "w")
            classement[i][1] = str(classement[i][1])
            classement[i][2] = str(classement[i][2])
            classement[i][3] = str(classement[i][3])
            classement[i][4] = str(classement[i][4])
            classement[i][5] = str(classement[i][5])
            file.write(" ".join(classement[i]) + "\n")
            file.close()
            add_logs(0,"[processing.elo_update] elo_update: creating cache file " + filename)
            upload_files(filename, folder_id)
            add_logs(0,"[processing.elo_update] elo_update: uploaded:" + filename + "  in: " + main_folder)
                    
            if os.path.exists(filename):
                os.remove(filename)
                add_logs(0,"[processing.elo_update] elo_update: deleting cache file " + filename)
            else:
                add_logs(1,"[processing.elo_update] elo_update: The file does not exist")
