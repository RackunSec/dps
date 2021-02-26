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

## Method: generate User IDs for Password spraying/phishing/etc:
def gen_uids(fs,csv_file,session,prompt_ui): # take a CSV and generate UIDs using a format specifier from the user
    try:
        with open(csv_file) as nfh: # names file handle
            for line in nfh: # loop over each line
                name = line.split(',') # split up the line
                if name[0] == "First": continue # we don't need the first line
                f_init = re.sub("^([A-Za-z]).*","\\1",name[0]).rstrip()
                l_init = re.sub("^([A-Za-z]).*","\\1",name[1]).rstrip()
                formatted = re.sub("%f",f_init,fs)
                formatted = re.sub("%l",l_init,formatted)
                formatted = re.sub("%F",name[0].rstrip(),formatted)
                formatted = re.sub("%L",name[1].rstrip(),formatted)
                print(formatted)
    except:
        error.msg("Could not open file: "+csv_file+" for reading.","dps_uid_gen",session,prompt_ui)
        return
