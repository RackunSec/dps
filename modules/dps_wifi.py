##############################################
## Custom DPS Module.
## Name: DPS Wi-Fi Monitor
## Description: Set Wi-Fi device into monitor mode with a single command.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
## TODO: Complete this!
##

## REQUIREMENTS:
def set(cmd,session,prompt_ui): # set an AC device into monitor mode using iw
    if len(cmd.split())==2:
        dev = cmd.split()[1]
        print("Set device "+dev+" into RFMON monitor mode.")
    else:
        session.help.msg("dps_wifi",session,prompt_ui)
