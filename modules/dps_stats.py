##############################################
## Custom DPS Module.
## Name: DPS Stats Tool.
## Description: Display stats on the ~/.dps directories.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import os

## Method: stats for shell logging
def show(prompt_ui):
    file_count = len(os.listdir(os.path.expanduser("~/.dps/logs/")))
    print(f"\n  • Log file count: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+str(file_count)+prompt_ui.bcolors['ENDC'])
    print(f"  • Log file location: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+os.path.expanduser("~/.dps/logs/")+prompt_ui.bcolors['ENDC'])
    line_count = int(0) # declare this
    for file in os.listdir(os.path.expanduser("~/.dps/logs/")):
        line_count += len(open(os.path.expanduser("~/.dps/logs/")+file).readlines())
    print(f"  • Total entries: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+str(line_count)+prompt_ui.bcolors['ENDC']+"\n")
