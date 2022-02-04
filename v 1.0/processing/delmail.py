
from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *
from utils.logs import *



def delmail(): 
    '''
    deleting mail forever on gmail
    '''
    delete_messages(default_search())
    add_logs(0,"[processing.delmai] delmail: deleting done")
