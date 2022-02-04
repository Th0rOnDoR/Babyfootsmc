
from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *

from datetime import date
import shutil
from shutil import make_archive
import os

def backup():
    """
    creating a file zip of root (folder where __main__.py is) and then uploading in to the backup folder in drive
    """
    if os.path.exists("__main__.py"): #always true
        service = service_drive() 
        today = str(date.today())
        src = os.path.realpath("__main__.py") #path
        add_logs(0,"[processing backup] backup: " +src) 
        root_dir, tail = os.path.split(src) #absolute path
        shutil.make_archive(today, "zip", root_dir) #make .zip
        upload_files(service, today + ".zip", "1tmivjqzmI7oCj2nKuaraAL7uAQStuQlC") #upload it
        
        if os.path.exists(today + ".zip"):
            os.remove(today + ".zip") #remove cache file
            add_logs(0,"[processingbackup] backup: deleting cache file ")
        else:
            add_logs(2,"[processing.backup] backup: The file does not exist. check if this non-existent have been upload")
            print("[processing.backup] backup: The file does not exist. check if this non-existent have been upload") 
            



