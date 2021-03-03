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

## Method: log the entered command:
def cmd(cmd,session): # logging a command to the log file:
    with open(session.LOG_FILENAME,'a') as log_file:
        log_file.write(str(datetime.datetime.now())+","+session.HOSTNAME+","+str(session.NET_DEV)+","+session.UID+","+getcwd()+","+cmd+"\n")
    return 0
