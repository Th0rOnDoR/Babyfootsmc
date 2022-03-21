# BabyFootSMC
is a elo rating program, from a mail with score data, it proceed and update every ranking 

# How to install 
    - works with python 3.6 (should work with 3.x but i havent test)
    - default python modules 
    - dependencies (for all versions):
        - tabulate
        - google-api-python-client 
        - google-auth-httplib2
        - google-auth-oauthlib
        You can install all dependencies with:
        ```pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib tabulate```
    - download the source code 

# How does it work ?
I'll now explain how it work for each version, and what changes between every version

## v0.1
The first woeking version. First, we get all email with a specific subject, the  extract the score and edit a file (elo.py)

## v0.2
import.py contains every import needed to run this version, every "processing" file is a fonction to do what follow. So, the utils folder contains every utility fonction like sendmail() and so on, then, this basic fonctions are used in processing files to do something (uploading files..) which are used in main.py to run the program.
I know i can remove a lot of import but, it was easier for me because i used pythonista and it reset all import everytime i run a script 

- adding drive:
    it upload a global ranking in a drive folder and create a personnal folder for each player where it upload a file with personnal score this time 
- adding delmail:
    it every mail received. Warning:  be sure to process every mail beforr delete them
    
## v0.3
A little upgrade because a few things doesnt work very well

## v0.4  
all processing file are now in a specific folder, it now store the number of goals, wins, loses, games of every player

- adding backup:
    It create a .zip file that contains all the code and stats files and it upload it in a specific folder on the drive.
    
- adding sendmail:
    It just send a mail to everyone, our profession adress finish by @smctab.com so i doesnt need to store an email form each player, only the name.

- adding sendcustom mail:
    It send a custom mail, ive used it to publish some poll, to be sure that everyone was good with the rules
    
## v0.5
Now, it doesnt send a mail to each player but only player who wants to receive mail (some players was used to look for their stats in history class, so, the teacher wasnt very happy so i disable some daily mail with this).

- adding Addacc (Add Account):
    An "account", someone who wants to receive mails
    
- adding delAcc (Delete Account):
    To remove an account

## v0.6
Basiclly the same thing but, ive some problems with the limitation of elo variation (+50/-50) so i tried to fix it here but seems like it doesnt work

# 1.0
i just add a new processing: mail error. It returns nothing, does nothing except if there is a "uncommun" mail in my mailbox. I fixed a lot of things in this versions.

## v1.1
I begin to add some commentary in every files. But, delta_elo doesnt want to work, like someone once said "I dont know why, i dont want to know why, i shouldnt have to wonder why but for whatever reason this thing wont work"


#Miscellaneous
The drive's link (not used anymore): 
Main folder: https://drive.google.com/drive/folders/19B8pLM-jO4F6YvlrZGP8S02PGCI6LEDo?usp=sharing
Backup: https://drive.google.com/drive/folders/1tmivjqzmI7oCj2nKuaraAL7uAQStuQlC?usp=sharing
