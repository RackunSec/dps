##############################################
## Custom DPS Module.
## Name: Aliasing commands.
## Description: Set an alias for a command as defined in ~/.dps/.dpsrc file.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
## TODO: Set/Update aliases.
##

## REQUIREMENTS:
def show(session,prompt_ui):
    print(prompt_ui.bcolors['BOLD']+"\n :: DPS.ini Defined [ALIASES] :: "+prompt_ui.bcolors['ENDC'])
    for alias in session.ALIASES:
        print(f"  • Alias found for {prompt_ui.bcolors['OKGREEN']}{alias}{prompt_ui.bcolors['ENDC']} as '{prompt_ui.bcolors['OKGREEN']}{session.ALIASES[alias]}{prompt_ui.bcolors['ENDC']}'")
    print("")
    return
