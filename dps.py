#!/usr/bin/env python3
# shell wrapper for superior logging
# logs as CSV with time,hostname,network:ip,who,command.
# requires Python 3+
#
# 2020 - Douglas Berdeaux

import readline
import os # for the commands, of course. These will be passed ot the shell.
import subprocess # for piping commands
import sys # for exit
import re # regexps
import ifaddr # NIC info
import socket # for HOSTNAME
import getpass # for logging the username
import datetime # for logging the datetime

ADAPTERS = ifaddr.get_adapters() # get network device info
NET_DEV = "" # store the network device
HOSTNAME = socket.gethostname() # hostname for logging
UID = getpass.getuser() # Get the username
REDIRECTION_PIPE = '_'
VERSION = "v0.10.6-12" # update this each time we push to the repo
LOG_DAY = datetime.datetime.today().strftime('%Y-%m-%d') # get he date for logging purposes
LOG_FILENAME = os.path.expanduser("~")+"/.dps/"+LOG_DAY+"_dps_log.csv" # the log file is based on the date
OWD=os.getcwd() # historical purposes

# Set up the log file directory:
if not os.path.exists(os.path.join(os.path.expanduser("~"),".dps")): # create the directory if it does not exist
    os.mkdir(os.path.join(os.path.expanduser("~"),".dps")) # mkdir
# Set up the log file itself:
if not os.path.exists(LOG_FILENAME):
    with open(LOG_FILENAME,'a') as log_file:
        log_file.write("When,Host,Network,Who,Where,What\n")
# Get the adapter and IP address:
for adapter in ADAPTERS: # loop through adapters
    if re.match("^e..[0-9]+",adapter.nice_name):
        NET_DEV = adapter.nice_name+":"+adapter.ips[0].ip
# colored output (does not work with the prompt - causes issues with line wrapping)
class bcolors:
    HEADER = '\033[95m'
    WHT = '\033[97m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\e[0m'

    #readline.parse_and_bind('set editing-mode vi')
    #readline.parse_and_bind('set horizontal-scroll-mode On') # will scroll horizontally, because wrapping is not working :/
readline.parse_and_bind('set colored-completion-prefix On') # colors types for TAB autocompletion.
readline.parse_and_bind('set colored-stats On') # colored tab-autocomplete file names (LS_COLORS)
    #readline.parse_and_bind('set completion-display-width 2') # columns to display auto completion options available # Not Working
readline.parse_and_bind('set expand-tilde On') # expand tilde? # Not working, I do this manually.
readline.parse_and_bind('set history-preserve-point On') # set the cursor point in history.
readline.parse_and_bind('set match-hidden-files On')
    #readline.parse_and_bind('set page-completions On')
    #readline.parse_and_bind('set print-completions-horizontally On')
readline.parse_and_bind('set show-all-if-ambiguous On')
    #readline.parse_and_bind('set skip-completed-text On')
    #readline.parse_and_bind('set visible-stats On')
readline.parse_and_bind('set mark-directories On') # for appending a slash # supposedly "On" by default, but not working.

def log_cmd(cmd): # logging a command to the log file:
    with open(LOG_FILENAME,'a') as log_file:
        log_file.write(str(datetime.datetime.now())+","+HOSTNAME+","+str(NET_DEV)+","+UID+","+os.getcwd()+","+cmd+"\n")
    return 0

# Define the help dialog:
def help():
    print("""
 -- \033[1mDemon Pentest Shell\033[0m --

 \033[1m:: Built-In Commands ::\033[0m
  • \033[1m\033[94mhelp\033[0m: this cruft.
  • \033[1m\033[94mstats\033[0m: all logging stats.
  • \033[1m\033[94mexit/quit\033[0m: return to terminal OS shell.

 \033[1m:: Keyboard Shortcuts ::\033[0m
  • \033[1m\033[94mCTRL+R\033[0m: Search command history.
  • \033[1m\033[94mCTRL+A\033[0m: Move cursor to beginning of line (similar to "HOME" key).
  • \033[1m\033[94mCTRL+P\033[0m: Place the previously ran command into the command line.
  • \033[1m\033[94mCTRL+B\033[0m: Move one character before cursor.
  • \033[1m\033[94mALT+F\033[0m:  Move one character forward.
  • \033[1m\033[94mCTRL+C/D\033[0m: Exit the shell gracefully.
    """)
    shell() # return to our shell() function to capture more input.

def run_cmd(cmd): # run a command. We capture a few and handle them, like "exit","quit","cd","sudo",etc:
    cmd_delta = cmd # the delta will be mangled user input as we see later:
    cmd_delta = re.sub("~",os.path.expanduser("~"),cmd_delta)
    cmd_delta = re.sub("^\s+","",cmd_delta) # remove any prepended spaces
    log_cmd(cmd_delta) # first, log the command.
    # Handle built-in commands:
    if (cmd_delta == "exit" or cmd_delta == "quit"):
        exit_gracefully()
        #sys.exit()
        #return 0
    elif(re.match("^\s?sudo",cmd_delta)): # for sudo, we will need the command's full path:
        sudo_regexp = re.compile("sudo ([^ ]+)")
        cmd_delta=re.sub(sudo_regexp,'sudo $(which \\1)',cmd_delta)
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd_delta])
        #print("DGB: CMD: '"+cmd_delta+"'")
        #sys.exit()
    elif(cmd_delta=="stats"):
        stats()
        shell()
    elif(cmd_delta=="help"):
        help()
    elif(cmd_delta=="version"):
        print(bcolors.OKGREEN+VERSION+bcolors.ENDC)
    elif(re.match("^ls",cmd_delta)):
        cmd_delta = re.sub("^ls","ls --color=auto",cmd)
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd_delta])
    elif(re.match("^cd",cmd_delta)):
        # TODO: make this a single re.sub() call:
        dir = re.sub('^cd\s+','',cmd_delta) # take off the path
        dir = re.sub('\s+$','',dir) # remove trailing spaces
        if (re.match("^cd(\s+)?",dir)): # go home
            dir = os.path.expanduser("~")
        if (dir==""):
            dir=os.path.expanduser("~")
        # changin directories using "-" and history:
        global OWD # our shell global needs referenced
        if (dir=="-"):
            BOWD=OWD # backup the OWD
            OWD=os.getcwd()
            os.chdir(BOWD)
            shell()
        else:
            OWD=os.getcwd() # store the directory that we are in for "-" purposes/historical
        if os.path.isdir(dir): # does it even exist?
            os.chdir(dir) # goto path
        else:
            print("PATH: "+bcolors.FAIL+'"'+dir+'"'+bcolors.ENDC+" does not exist.")
    else:
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd_delta])
    shell() # or else return to shell

def exit_gracefully():
        #ans = input(bcolors.FAIL+"\n[!] CTRL+C DETECTED\n[?] Do you wish to quit the Demon Pentest Shell (y/n)? "+bcolors.ENDC)
        ans = input(bcolors.FAIL+"\n[?]"+bcolors.ENDC+" Do you wish to quit the Demon Pentest Shell (y/n)? ")
        if ans == "y":
            print("[+] Quitting Demon Penetst Shell. File logged: "+LOG_FILENAME)
            sys.exit(1)
        else:
            shell()

def list_folder(path):
    PATHS=os.getenv('PATH').split(":")
    """
    Lists folder contents
    """
    # starts with "/"
    if path.startswith(os.path.sep):
        # absolute path
        basedir = os.path.dirname(path)
        contents = os.listdir(basedir)
        # add back the parent
        contents = [os.path.join(basedir, d) for d in contents]
    else:
        # absolute (home) path:
        if path.startswith("~/"):
            contents = os.listdir(os.path.expanduser("~/"))
        else:
            # This could be a command so try paths:
            # TODO get environment $PATH's and break them up testing each one:
            contents=os.listdir(os.curdir)
            for item in contents:
                if re.match(path,item):
                    return contents
            for path_entry in PATHS:
                try: # just learnt my first try/catch in Python - woohoo! :D
                    contents+=os.listdir(path_entry)
                except:
                    pass
    return contents

# stats for shell logging
def stats():
    file_count = len(os.listdir(os.path.expanduser("~/.dps/")))
    print(bcolors.OKBLUE+" "+bcolors.BOLD+" [i] DPS Logging Stats: "+bcolors.ENDC)
    print("  • Log file count: "+str(file_count)+bcolors.ENDC)
    print("  • Log file location: "+os.path.expanduser("~/.dps/"))
    line_count = int(0) # declare this
    for file in os.listdir(os.path.expanduser("~/.dps/")):
        line_count += len(open(os.path.expanduser("~/.dps/")+file).readlines())
    print("  • Total entries: "+str(line_count)+bcolors.ENDC)

# Our custom completer function:
def completer(text, state):
    """
    Our custom completer function
    """
    if text == "~/":
        text = os.path.expanduser("~/")
    options = [x for x in list_folder(text) if x.startswith(text)]
    return options[state]

# REQUIRED:
#readline.set_completer()
readline.set_completer(completer)
readline.parse_and_bind('tab: complete')
#readline.set_completer_delims('~ \t\n`!@#$%^&*()-=+[{]}\\|;:\'",<>?')
readline.set_completer_delims(' \t\n')

def shell():
    try:
        # Build out the prompt fo rthe user:
        PATHS=os.getenv('PATH').split(":")
        if UID == "root":
            prompt_tail = "# "
        else:
            prompt_tail = "> " # added promt indicator for root
        prompt = UID+"@"+HOSTNAME+":"+os.getcwd()+"(dps)"+prompt_tail
        #last_string = input(UID+bcolors.BOLD+"@"+bcolors.ENDC+HOSTNAME+bcolors.BOLD+"["+bcolors.ENDC+os.getcwd()+bcolors.BOLD+"]"+">> "+bcolors.ENDC)
        last_string = input(prompt)
        run_cmd(last_string)
    except KeyboardInterrupt:
        exit_gracefully()
    except EOFError:
        exit_gracefully()

print(bcolors.BOLD+"\n *** Welcome to the Demon Pentest Shell ("+VERSION+")\n *** Type \"exit\" to return to standard shell.\n"+bcolors.ENDC)

shell() # start the app
