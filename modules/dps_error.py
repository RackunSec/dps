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
    print(f"{prompt_ui.bcolors['BOLD']}[?]{prompt_ui.bcolors['FAIL']}{prompt_ui.bcolors['ENDC']}{prompt_ui.bcolors['FAIL']} ¬_¬ wut? -- "+msg+f"{prompt_ui.bcolors['ENDC']}")
    if cmd != "":
        help.msg(cmd,session,prompt_ui) # show the He\lp dialog from the listings above
