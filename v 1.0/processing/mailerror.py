from utils.mail import *
from utils.elo_utilities import *
from utils.match_utilities import *
from utils.drive import *
from utils.logs import *
from utils.cte import *

def mailerror():
    result = search_messages("Mail Delivery Subsystem")
    if result != []:
        add_logs(0,"[processing.mailerror] mailerror: done")
        return
    else:
        add_logs(1,"[processing.mailerror] mailerror: something to see")
        return
    
