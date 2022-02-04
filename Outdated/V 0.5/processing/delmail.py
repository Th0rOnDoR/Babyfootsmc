
from utils.mail import *
from utils.match_utilities import *
from utils.elo_utilities import *
from utils.drive import *


def delmail(): 
    '''
    deleting mail forever on gmail
    '''
    delete_messages("Subject:CLASSEMENT in:inbox")
    print("[processing.delmai] delmail: deleting done")
