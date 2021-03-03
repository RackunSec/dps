##############################################
## Custom DPS Module.
## Name: Error Handling.
## Description: Display errors gracefully.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import dps_error as error
import re

## Method: generate User IDs for Password spraying/phishing/etc:
def gen_uids(cmd,session,prompt_ui): # take a CSV and generate UIDs using a format specifier from the user
    FAIL=prompt_ui.bcolors['FAIL']
    ENDC=prompt_ui.bcolors['ENDC']
    args = cmd.split()
    if len(args)!=3:
        print(f"\n{FAIL}Not enough arguments for dps_uid_gen. See below.{ENDC}")
        session.help.msg("dps_uid_gen",session,prompt_ui)
    else:
        csv_file=cmd.split()[2]
        fs=cmd.split()[1]
        if not re.search("%[^%]+",fs):
            print(f"\n{FAIL}Format Specifier has incorrect syntax. See below.")
            session.help.msg("dps_uid_gen",session,prompt_ui)
        else:
            try:
                with open(csv_file) as nfh: # names file handle
                    for line in nfh: # loop over each line
                        name = line.split(',') # split up the line
                        if name[0] == "First": continue # we don't need the first line
                        f_init = re.sub("^\s*","",name[0]).rstrip()
                        l_init = re.sub("^\s*","",name[1]).rstrip()
                        f_init = re.sub("^([A-Za-z]).*","\\1",f_init)
                        l_init = re.sub("^([A-Za-z]).*","\\1",l_init)
                        f_full = re.sub(r"\s+","",name[0]).rstrip()
                        l_full = re.sub(r"\s+","",name[1]).rstrip()
                        formatted = re.sub("%f",f_init,fs)
                        formatted = re.sub("%l",l_init,formatted)
                        formatted = re.sub("%F",f_full,formatted)
                        formatted = re.sub("%L",l_full,formatted)
                        print(formatted)
            except:
                print(f"\n{FAIL}Could not open file, or file is not a CSV: {csv_file} for reading.{ENDC}")
                session.help.msg("dps_uid_gen",session,prompt_ui)
                return
