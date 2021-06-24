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
from os import listdir
from os.path import expanduser
from re import split as resplit # regexp splitting


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

def import_history(dps,session,logfile,prompt_ui):
    GREEN = prompt_ui.bcolors['GREEN']
    FAIL = prompt_ui.bcolors['FAIL']
    OKGREEN = prompt_ui.bcolors['OKGREEN']
    ENDC = prompt_ui.bcolors['ENDC']
    if logfile != "": # we passed in a log file:
        if logfile == "all": # just import all of them
            print(f"{OKGREEN}{ENDC} Importing all logs")
            for file in listdir(expanduser("~/.dps/logs")):
                file_path = expanduser("~/.dps/logs/")+file
                print(f"{OKGREEN}{ENDC} Importing logs from: {file_path}")
                with open(file_path) as file_log:
                    for entry in file_log:
                        entry = entry.rstrip()
                        #print(f"[dbg] entry: {entry}") # DEBUG
                        if len(entry)>=5:
                            cmd = resplit(r'[^\\],',entry)[5]
                            if cmd != "" and cmd != "What": # remove CSV line head
                                cmd_clean = cmd.rstrip()
                                cmd_clean = re.sub("\\\+,",",",cmd_clean) # This is to clean the CSV file's backslashes of the commas for our command history.
                                dps.prompt_session.history.append_string(cmd_clean)
            return # all done.
        print(f"{OKGREEN}{ENDC} Importing log: {logfile}")
        with open(logfile) as file:
            for entry in file:
                entry = entry.rstrip()
                cmd = resplit(r'[^\\],',entry)[5]
                if cmd != "" and cmd != "What": # remove CSV line head
                    cmd_clean = cmd.rstrip()
                    cmd_clean = re.sub("\\\+,",",",cmd_clean) # This is to clean the CSV file's backslashes of the commas for our command history.
                    dps.prompt_session.history.append_string(cmd_clean)
        return # all done.
    else: # we are simply entering all entries from the current day's logfile:
        with open(session.LOG_FILENAME) as file:
            for entry in file:
                entry = entry.rstrip()
                cmd = resplit(r'[^\\],',entry)[5]
                if cmd != "" and cmd != "What": # remove CSV line head
                    cmd_clean = cmd.rstrip()
                    cmd_clean = re.sub("\\\+,",",",cmd_clean) # This is to clean the CSV file's backslashes of the commas for our command history.
                    dps.prompt_session.history.append_string(cmd_clean)
        return # all done.
    return

def import_log(session,prompt_ui,dps):
    GREEN = prompt_ui.bcolors['GREEN']
    FAIL = prompt_ui.bcolors['FAIL']
    OKGREEN = prompt_ui.bcolors['OKGREEN']
    ENDC = prompt_ui.bcolors['ENDC']
    print(f"{OKGREEN}{ENDC} Choose a log file below to import into history:")
    token = 0
    logs = {}
    listdir(expanduser("~"))
    for log_file in listdir(expanduser("~/.dps/logs")):
        logs[token]=log_file
        token+=1
    for log_file in logs:
        print(f"[{log_file}]: {logs[log_file]}")
    print("[all] import ALL log's entries")
    ans = input("\nChoose a number: ")
    if ans == "all":
        import_history(dps,session,"all",prompt_ui)
    elif int(ans) in logs:
        import_history(dps,session,expanduser("~")+"/.dps/logs/"+logs[int(ans)],prompt_ui)
    else:
        print(f"{FAIL} Your entry was not in the list.{ENDC}")
        import_log(prompt_ui,dps)
