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

## Method: do the scrape! we do the web page scrape!
def comment_scrape(session,prompt_ui,uri):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    print(f"[*] Fetching: {uri}\n")
    req_data = requests.get(uri, stream=True)
    code_count = 0
    mlc = 0
    for code in req_data.iter_lines():
        line = str(code, 'utf-8')
        if re.search('//',line): # JS comment
            print(f"[{str(code_count)}]: {line.rstrip()}")
        if (mlc == 1): # we are in a multi-line comment
            if re.match(".*-->",line) or re.match(".*\*/\s?$",line): # end of multi-line comment
                print(f"[{str(code_count)}]: {line.rstrip()}")
                mlc = 0 # reset, exit the multi-line comment
            else:
                print(f"[{str(code_count)}]: {line.rstrip()}")
        if (re.match(".*<!--",line)
            or re.match("^\s+//",line)
            or re.match(".*/\*",line)):
            if(re.match(".*<!--\s?$",line) or re.match(".*/\*\s?$",line)):
                print(f"[{str(code_count)}]: {line.rstrip()}")
                mlc = 1 # Multi line comment token
            else:
                print(f"[{str(code_count)}]: {line.rstrip()}")
        code_count += 1
    print("\n") # done
