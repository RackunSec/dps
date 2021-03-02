##############################################
## Custom DPS Module.
## Name: DPS->WWW->Comment Scrape.
## Description: Will request a web page and display all discovered HTML and JS Comments.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import sys
import re
import requests

## Method: do the scrape! we do the web page (FOR COMMENTS) scrape!
def comment_scrape(session,prompt_ui,uri):
    GRN = prompt_ui.bcolors['OKGREEN']
    BOLD = prompt_ui.bcolors['BOLD']
    CMNT = prompt_ui.bcolors['COMMENT']
    ENDC = prompt_ui.bcolors['ENDC']
    UNDER = prompt_ui.bcolors['UNDER']
    ITAL = prompt_ui.bcolors['ITAL']
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    print(f"{BOLD}\n[*] Fetching: {ENDC}{ITAL}{UNDER}{uri}{ENDC}\n")
    req_data = requests.get(uri, stream=True)
    code_count = 0
    code_count_color = ""
    mlc = 0
    for code in req_data.iter_lines():
        line = str(code, 'utf-8')
        if re.search('//',line): # JS comment
            print(f"{code_count_color}: {CMNT}{line.rstrip()}{ENDC}")
        if (mlc == 1): # we are in a multi-line comment
            if re.match(".*-->",line) or re.match(".*\*/\s?$",line): # end of multi-line comment
                print(f"{code_count_color}: {CMNT}{line.rstrip()}{ENDC}")
                mlc = 0 # reset, exit the multi-line comment
            else:
                print(f"{code_count_color}: {CMNT}{line.rstrip()}{ENDC}")
        if (re.match(".*<!--",line)
            or re.match("^\s+//",line)
            or re.match(".*/\*",line)):
            if(re.match(".*<!--\s?$",line) or re.match(".*/\*\s?$",line)):
                print(f"{code_count_color}: {CMNT}{line.rstrip()}{ENDC}")
                mlc = 1 # Multi line comment token
            else:
                print(f"{code_count_color}: {CMNT}{line.rstrip()}{ENDC}")
        code_count += 1
        code_count_color = CMNT+str(code_count)+ENDC
    print("\n") # done
