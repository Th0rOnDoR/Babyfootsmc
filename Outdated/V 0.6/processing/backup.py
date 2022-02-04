
from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *

from datetime import date
import shutil
from shutil import make_archive
import os

def backup():
    '''
    creating a file zip of root and then uploading in to the backup folder in drive
    '''
    if os.path.exists("__main__.py"):
        today = str(date.today())
        src = os.path.realpath("__main__.py")
        print("[processing backup] backup: " +src)
        root_dir, tail = os.path.split(src)
        shutil.make_archive(today, "zip", root_dir)
        upload_files(today + ".zip", "1tmivjqzmI7oCj2nKuaraAL7uAQStuQlC")
        
        if os.path.exists(today + ".zip"):
            os.remove(today + ".zip")
            print("[processingbackup] backup: deleting cache file ")
        else:
            print("[processing.backup] backup: The file does not exist")
            



