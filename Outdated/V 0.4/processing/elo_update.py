from datetime import date
from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *


def elo_update():
    '''
    creating a file of ranking then uploading it into main folder 
    for each player, creating a file and then uploading it into the folder of the player to see player's rating evolution
    '''
    service = get_gdrive_service() #getting drive service
    main_folder = '19B8pLM-jO4F6YvlrZGP8S02PGCI6LEDo' #not root folder on drive but the sharing folder
    score_folder= '1KeClK1KHFt70ZMmOv9XxpMPd8DqD_HgX' #score folder to put every player stats
    today = str(date.today()) # to name the file
    print("[processing.elo_update] elo_update: today: " + today) 
    
    classement = get_classement()
    filename = "classement general.txt"
    print("[processing.elo_update] elo_update: filename: " + filename)   
    file = open(filename, "w") 
    file.write(tabulate(classement, headers=["Joueur", "Points ", "Parties", "Victoire", "Winstreak", "Total goal"]))
    file.close()
    upload_files(filename, main_folder) #uploading file then we'll delete it
    print("[processing.elo_update] elo_update: uploaded:" + filename + "  in: " + main_folder)
    
    if os.path.exists(filename): #delete if exist
        os.remove(filename)
        print("[processing.elo_update] elo_update: deleting cache file " + filename)
    else: #else, no need, it doesnt exist
        print("[processing.elo_update] elo_update: The file does not exist") 
    
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
            print("[processing.elo_update] elo_update: creating cache file " + filename)
            file = open(filename, "w")
            classement[i][1] = str(classement[i][1])
            classement[i][2] = str(classement[i][2])
            classement[i][3] = str(classement[i][3])
            classement[i][4] = str(classement[i][4])
            classement[i][5] = str(classement[i][5])
            file.write(" ".join(classement[i]) + "\n") #create a file with only one line witb player's stats
            file.close()
            upload_files(filename, folder_id)
            print("[processing.elo_update] elo_update: uploaded:" + filename + "  in: " + folder_id)
                
            if os.path.exists(filename): # deleting file as previous 
                os.remove(filename)
                print("[processing.elo_update] elo_update: deleting cache file " + filename)
            else:
                print("[processing.elo_update] elo_update: The file does not exist")
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
            print("[processing.elo_update] elo_update: creating cache file " + filename)
            upload_files(filename, folder_id)
            print("[processing.elo_update] elo_update: uploaded:" + filename + "  in: " + main_folder)
                    
            if os.path.exists(filename):
                os.remove(filename)
                print("[processing.elo_update] elo_update: deleting cache file " + filename)
            else:
                print("[processing.elo_update] elo_update: The file does not exist")
