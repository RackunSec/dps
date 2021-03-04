##############################################
## Custom DPS Module.
## Name: Aliasing commands.
## Description: Set an alias for a command as defined in ~/.dps/.dpsrc file.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
## TODO: Set/Update aliases.
##

## REQUIREMENTS:
import os # for path class
from os.path import expanduser # for home directory
import time # for timestamp

## Method: overwrite every byte in file with garbage byte, rename and unlink from FS:
def self_destruct(session,prompt_ui):
    ENDC=prompt_ui.bcolors['ENDC']
    BOLD=prompt_ui.bcolors['BOLD']
    OKGREEN=prompt_ui.bcolors['OKGREEN']
    WARN=prompt_ui.bcolors['WARN']
    INFO=prompt_ui.bcolors['INFO']
    QUESTION=prompt_ui.bcolors['QUESTION']
    print(f"{WARN}WARNING - THIS WILL DESTROY ALL LOG FILES: ~/.dps/logs/* !! {ENDC}")
    ans = input(f"{QUESTION} Continue? (y/N): {ENDC}")
    if ans=="y" or ans=="Y":
        # destroy em:
        ENDC=prompt_ui.bcolors['ENDC']
        OKGREEN=prompt_ui.bcolors['OKGREEN']
        FAIL=prompt_ui.bcolors['FAIL']
        BOLD=prompt_ui.bcolors['BOLD']
        for file in os.listdir(expanduser("~")+"/.dps/logs/"):
            file_path = expanduser("~")+"/.dps/logs/"+file
            file_size = os.path.getsize(file_path)
            print(f"{FAIL}[!] Destroying log {file_path} ({file_size} bytes)",end="\t")
            # for 0 - file_size: overwrite with zeros before unlinking:
            f = open(file_path,'wb')
            i = 0
            while i <= file_size:
                f.write(b"00110000")
                i+=1
            f.close()
            path_to = os.path.dirname(os.path.abspath(file_path))
            new_file_name = path_to+"/"+'destroyed_'+str(time.time())+".nothing"
            os.rename(file_path,new_file_name) # rename it to garbage
            os.unlink(new_file_name) # unlink it from FS
            print(f"{ENDC}{BOLD}[ {OKGREEN}OK{ENDC}{BOLD} ]{ENDC}")
        print(f"{INFO} All log files have been shredded. Logging out.{ENDC}")
        os.sys.exit()
        return
    else:
        return
