#!/usr/bin/env python3
# shell wrapper for superior logging
# logs as CSV with time,hostname,network:ip,who,command.
# requires Python 3+
#
# 2020 - Douglas Berdeaux

import configparser # dps.conf from ~/.dps/
import os # for the commands, of course. These will be passed ot the shell.
import subprocess # for piping commands
import sys # for exit
import re # regexps
import ifaddr # NIC info
import socket # for HOSTNAME
import getpass # for logging the username
import datetime # for logging the datetime
from prompt_toolkit import prompt, ANSI # for input
from prompt_toolkit.completion import WordCompleter # completer function (feed a list)
from prompt_toolkit import PromptSession

###===========================================
## GLOBAL VALUES:
###===========================================
ADAPTERS = ifaddr.get_adapters() # get network device info
NET_DEV = "" # store the network device
HOSTNAME = socket.gethostname() # hostname for logging
UID = getpass.getuser() # Get the username
REDIRECTION_PIPE = '_' # TODO not needed?
VERSION = "v0.10.7-2" # update this each time we push to the repo
LOG_DAY = datetime.datetime.today().strftime('%Y-%m-%d') # get he date for logging purposes
LOG_FILENAME = os.path.expanduser("~")+"/.dps/"+LOG_DAY+"_dps_log.csv" # the log file is based on the date
CONFIG_FILENAME = os.path.expanduser("~")+"/.dps/dps.ini" # config (init) file name
CONFIG = configparser.ConfigParser() # config object
OWD=os.getcwd() # historical purposes
# Add all built-in commands here so they populate in the tab-autocompler:
BUILTINS=['dps_stats','dps_uid_gen','dps_wifi_mon','dps_config']
PRMPT_STYL=0 # Prompt style setting
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
    GRYBG = '\033[100m'
    LGHTGRY='\033[37m'
    ORNG = '\e033[220m'

###===========================================
## PRELIMINARY FILE/DESCRIPTOR WORK:
###===========================================
if not os.path.exists(os.path.join(os.path.expanduser("~"),".dps")): # create the directory if it does not exist
    os.mkdir(os.path.join(os.path.expanduser("~"),".dps")) # mkdir
# Set up the log file itself:
if not os.path.exists(LOG_FILENAME):
    with open(LOG_FILENAME,'a') as log_file:
        log_file.write("When,Host,Network,Who,Where,What\n")
# Set up the config file/pull values:
if not os.path.exists(CONFIG_FILENAME):
    # Add the file
    with open(CONFIG_FILENAME,'a') as config_file:
        ### ADD ALL CONFIG STUFF HERE:
        config_file.write("[Style]\n")
        config_file.write("PRMPT_STYL = 0\n")
        print(f"{bcolors.FAIL}[!] Configuration file generated, please restart shell.{bcolors.ENDC}")
        sys.exit(1)
else:
    # Config file exists, grab the values using configparser:
    CONFIG.read(CONFIG_FILENAME) # read the file
    CONFIG.sections() # get all sections of the config
    if 'Style' in CONFIG:
        # print(f"CONFIG['Style']['PRMPT_STYL']: "+CONFIG['Style']['PRMPT_STYL']) # DEBUG
        PRMPT_STYL = int(CONFIG['Style']['PRMPT_STYL']) # grab the value of the style
    else:
        print(f"{bcolors.FAIL}[!]{bcolors.ENDC} Error in config file")
        sys.exit() # die
    # TODO else: # add it
# Get the adapter and IP address:
for adapter in ADAPTERS: # loop through adapters
    if re.match("^e..[0-9]+",adapter.nice_name):
        NET_DEV = adapter.nice_name+":"+adapter.ips[0].ip
def log_cmd(cmd): # logging a command to the log file:
    with open(LOG_FILENAME,'a') as log_file:
        log_file.write(str(datetime.datetime.now())+","+HOSTNAME+","+str(NET_DEV)+","+UID+","+os.getcwd()+","+cmd+"\n")
    return 0

###===========================================
## CUSTOM HELP DIALOGS:
###===========================================
def help(cmd_name):
    if cmd_name != "":
        if cmd_name == "dps_uid_gen":
                print("""
    -- \033[1mDPS UID Generator Usage\033[0m --

      \033[1m\033[94mdps_uid_gen \033[0m(format specifier) (csv file)

      :: \033[1mFormat Specifiers\033[0m ::
      • \033[1m\033[94m%F\033[0m: First Name.
      • \033[1m\033[94m%f\033[0m: First Initial.
      • \033[1m\033[94m%L\033[0m: Last Name.
      • \033[1m\033[94m%l\033[0m: Last Initial.

      You can add anything else you wish, such as,
       e.g: %f.%L123@client.org
       result: j.doe123@client.org
                    """)
        elif cmd_name == "dps_wifi_mon":
            print("""
    -- \033[1mDPS Wi-Fi Monitor Mode\033[0m --

      \033[1m\033[94mdps_wifi_mon \033[0m(wi-fi device)

      :: \033[1mRequirements\033[0m ::
      • \033[1m\033[94miw\033[0m
      • \033[1m\033[94mairmon-ng\033[0m
      • \033[1m\033[94mifconfig\033[0m
            """)
        elif cmd_name == "dps_config":
            print("""
        -- \033[1mDPS Configuration Settings\033[0m --

          \033[1m\033[94mdps_config \033[0mprompt (integer (0-9))
            """)
    else:
        print("""
     -- \033[1mDemon Pentest Shell\033[0m --

     \033[1m:: Built-In Commands ::\033[0m
      • \033[1m\033[94mhelp\033[0m: this cruft.
      • \033[1m\033[94mdps_stats\033[0m: all logging stats.
      • \033[1m\033[94mdps_uid_gen\033[0m: generate UIDs using "Firstname,Lastname" CSV file.
      • \033[1m\033[94mdps_wifi_mon\033[0m: Set Wi-Fi radio to RFMON.
      • \033[1m\033[94mdps_config\033[0m: Set prompt and shell options.
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

###===========================================
## COMMAND HOOKS:
###===========================================
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
    elif(cmd_delta.startswith("dps_wifi_mon")):
        args = cmd_delta.split()
        if len(args)>1:
            dps_wifi_mon(args[1]) # should be the device
        else:
            help("dps_wifi_mon")
    elif(re.match("^\s?sudo",cmd_delta)): # for sudo, we will need the command's full path:
        sudo_regexp = re.compile("sudo ([^ ]+)")
        cmd_delta=re.sub(sudo_regexp,'sudo $(which \\1)',cmd_delta)
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd_delta])
    elif(cmd_delta.startswith("dps_uid_gen")):
        args = cmd_delta.split()
        if len(args)==3:
            dps_uid_gen(args[1],args[2]) # should be "format specifier, filename"
        else:
            help("dps_uid_gen")
    elif(cmd_delta=="dps_stats"):
        dps_stats()
        shell()
    elif(cmd_delta.startswith("dps_config")):
        args = re.sub("dps_config","",cmd_delta).split() # make an array
        if len(args) > 1:
            dps_config(args)
        else:
            help("dps_config")
    elif(cmd_delta.startswith("help")):
        args = cmd_delta.split()
        if(len(args)>1):
            help(args[1])
        else:
            help("")
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

###===========================================
## DPS CUSTOM BUILT-IN SHELL CMD METHODS:
###===========================================
def dps_update_config(args):
    global CONFIG # declare the global
    global CONFIG_FILENAME # config file name from global
    if len(args) > 1:
        if args[0] == "prompt": # set it in the config file:
            #try:
            print(f"{bcolors.OKBLUE}[*]{bcolors.ENDC} Adding "+str(args[1])+" as PRMPT_STYL in "+CONFIG_FILENAME)
            CONFIG.set('Style','PRMPT_STYL',args[1]) # TODO int() ?
            with open(CONFIG_FILENAME, 'w') as config_file:
                CONFIG.write(config_file)
            #except:
                #print(f"{bcolors.FAIL}[!] ERROR setting value in ini file.{bcolors.ENDC}")

def dps_config(args): # configure the shell
    global PRMPT_STYL # this is the prompt color setting
    if args[0] == "prompt" and args[1] != "":
        PRMPT_STYL = int(args[1])
        # Now set it for session / preference in the dps.ini file:
        dps_update_config(args)
    else:
        print("Usage: dps_config prompt [0-9] for new prompt.")
    shell()
def dps_wifi_mon(dev): # set an AC device into monitor mode using iw
    print("Set device "+dev+" into RFMON monitor mode.")
# stats for shell logging
def dps_stats():
    file_count = len(os.listdir(os.path.expanduser("~/.dps/")))
    print(bcolors.BOLD+"\n :: DPS Logging Stats :: "+bcolors.ENDC)
    print("  • Log file count: "+bcolors.BOLD+bcolors.OKBLUE+str(file_count)+bcolors.ENDC)
    print("  • Log file location: "+bcolors.BOLD+bcolors.OKBLUE+os.path.expanduser("~/.dps/")+bcolors.ENDC)
    line_count = int(0) # declare this
    for file in os.listdir(os.path.expanduser("~/.dps/")):
        line_count += len(open(os.path.expanduser("~/.dps/")+file).readlines())
    print("  • Total entries: "+bcolors.BOLD+bcolors.OKBLUE+str(line_count)+bcolors.ENDC+"\n")
def dps_uid_gen(fs,csv_file): # take a CSV and generate UIDs using a format specifier from the user
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
        print(bcolors.FAIL+"[!]"+bcolors.ENDC+" Could not open file: "+csv_file+" for reading.")
    shell() # return to shell

###===========================================
## GENERAL METHODS FOR HANDLING THINGS:
###===========================================
def exit_gracefully(): # handle CTRL+C or CTRL+D, or quit, or exit gracefully:
        #ans = input(bcolors.FAIL+"\n[!] CTRL+C DETECTED\n[?] Do you wish to quit the Demon Pentest Shell (y/n)? "+bcolors.ENDC)
        ans = input(bcolors.FAIL+"\n[?]"+bcolors.ENDC+" Do you wish to quit the Demon Pentest Shell (y/n)? ")
        if ans == "y":
            print("[+] Quitting Demon Penetst Shell. File logged: "+LOG_FILENAME)
            sys.exit(1)
        else:
            shell()

def list_folder():
    PATHS=os.getenv('PATH').split(":")
    contents = os.listdir(os.getcwd())#.append(BUILTINS) # declare array (and define with current dir contents)
    # TODO add logic to remove duplicate arrays
    for path in PATHS:
        try:
            contents+=os.listdir(path)
        except:
            continue
    return contents

# Our custom completer function:
#def completer(text, state):
    """
    Our custom completer function
    """
session = PromptSession() # session is global
def shell():
    global session
    try:
        # Build out the prompt fo rthe user:
        PATHS=os.getenv('PATH').split(":")
        if UID == "root":
            prompt_tail = "# "
        else:
            prompt_tail = "> " # added promt indicator for root
        if PRMPT_STYL == 0: # Matt's Prompt:
            prompt_txt = f"{bcolors.FAIL}{bcolors.BOLD}{UID}@{HOSTNAME}{bcolors.ENDC}:{bcolors.OKBLUE}{bcolors.BOLD}{os.getcwd()}{bcolors.WARNING}(dps){bcolors.ENDC}{prompt_tail}"
        elif PRMPT_STYL == 1: # Doug's prompt:
            prompt_txt = f"{bcolors.BOLD}{UID}{bcolors.ENDC}{bcolors.WHT}@{bcolors.ENDC}{bcolors.LGHTGRY}{HOSTNAME}{bcolors.ENDC}{bcolors.BOLD}{bcolors.WHT}:{bcolors.ENDC}{bcolors.LGHTGRY}{os.getcwd()}{bcolors.BOLD}{bcolors.WHT}(dps){prompt_tail}{bcolors.ENDC}"
        else: # Default prompt:
            prompt_txt = f"{bcolors.FAIL}{bcolors.BOLD}{UID}@{HOSTNAME}{bcolors.ENDC}:{bcolors.OKBLUE}{bcolors.BOLD}{os.getcwd()}{bcolors.WARNING}(dps){bcolors.ENDC}{prompt_tail}"

        tab_complete=WordCompleter(list_folder())
        last_string = session.prompt(ANSI(prompt_txt),completer=tab_complete) # fixes text-wrapping issue experenced with input()
        run_cmd(last_string)
    except KeyboardInterrupt:
        exit_gracefully()
    except EOFError:
        exit_gracefully()

###===========================================
## START THE SHELL:
###===========================================
print(bcolors.BOLD+"\n *** Welcome to the Demon Pentest Shell ("+VERSION+")\n *** Type \"exit\" to return to standard shell.\n"+bcolors.ENDC)
shell() # start the app
