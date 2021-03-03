##############################################
## Custom DPS Module.
## Name:
## Description:
## Author:
## Author URL:
##
##

## REQUIREMENTS:
import dps_help as help

## Method: Display error gracefully:
def msg(msg,cmd,session,prompt_ui):
    FAIL=prompt_ui.bcolors['FAIL']
    ENDC=prompt_ui.bcolors['ENDC']
    print(f"{FAIL}"+msg+f"{ENDC}")
    if cmd != "":
        help.msg(cmd,session,prompt_ui) # show the He\lp dialog from the listings above
