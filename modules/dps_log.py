##############################################
## Custom DPS Module.
## Name: Logging Module.
## Description: All log-related methods go here.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import datetime
from os import getcwd
import re

## Method: log the entered command:
def cmd(cmd,session,prompt_ui): # logging a command to the log file:
    cmd = re.sub(",",r"\\,",cmd)
    try:
        with open(session.LOG_FILENAME,'a') as log_file:
            log_file.write(str(datetime.datetime.now())+","+session.HOSTNAME+","+str(session.NET_DEV)+","+session.UID+","+getcwd()+","+cmd+"\n")
        return 0
    except:
        print(f"{FAIL}Could not open {session.LOGNAME} for reading / writing!")
        sys.exit()
