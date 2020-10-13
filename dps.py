#!/usr/bin/env python3
# shell wrapper for superior logging
# logs as CSV with time,hostname,network:ip,who,command.
# requires Python 3+
#
# 2020 - Douglas Berdeaux, Matthew Creel

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
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.styles import Style # Style the prompt
import shlex # Splitting by spaces into a list

###===========================================
## GLOBAL VALUES:
###===========================================
ADAPTERS = ifaddr.get_adapters() # get network device info
NET_DEV = "" # store the network device
HOSTNAME = socket.gethostname() # hostname for logging
UID = getpass.getuser() # Get the username
REDIRECTION_PIPE = '_' # TODO not needed?
VERSION = "v0.10.14-7" # update this each time we push to the repo
LOG_DAY = datetime.datetime.today().strftime('%Y-%m-%d') # get he date for logging purposes
LOG_FILENAME = os.path.expanduser("~")+"/.dps/"+LOG_DAY+"_dps_log.csv" # the log file is based on the date
CONFIG_FILENAME = os.path.expanduser("~")+"/.dps/dps.ini" # config (init) file name
CONFIG = configparser.ConfigParser() # config object
OWD=os.getcwd() # historical purposes
# Add all built-in commands here so they populate in the tab-autocompler:
BUILTINS=['dps_stats','dps_uid_gen','dps_wifi_mon','dps_config']
PRMPT_STYL=0 # Prompt style setting
prompt_tail = "# " if UID == "root" else "> " # diff root prompt
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
                print(f"""
    -- {bcolors.WHT}{bcolors.BOLD}DPS UID Generator Usage{bcolors.ENDC} --

      {bcolors.BOLD}{bcolors.OKBLUE}dps_uid_gen {bcolors.ENDC}(format specifier) (csv file)

      :: {bcolors.BOLD}Format Specifiers{bcolors.ENDC} ::
      • {bcolors.BOLD}{bcolors.OKBLUE}%F{bcolors.ENDC}: First Name.
      • {bcolors.BOLD}{bcolors.OKBLUE}%f{bcolors.ENDC}: First Initial.
      • {bcolors.BOLD}{bcolors.OKBLUE}%L{bcolors.ENDC}: Last Name.
      • {bcolors.BOLD}{bcolors.OKBLUE}%l{bcolors.ENDC}: Last Initial.

      You can add anything else you wish, such as,
       e.g: %f.%L123@client.org
       result: j.doe123@client.org
                    """)
        elif cmd_name == "dps_wifi_mon":
            print(f"""
    -- {bcolors.BOLD}DPS Wi-Fi Monitor Mode{bcolors.ENDC} --

      {bcolors.BOLD}{bcolors.OKBLUE}dps_wifi_mon {bcolors.ENDC}(wi-fi device)

      :: {bcolors.BOLD}Requirements{bcolors.ENDC} ::
      • {bcolors.BOLD}{bcolors.OKBLUE}iw{bcolors.ENDC}
      • {bcolors.BOLD}{bcolors.OKBLUE}airmon-ng{bcolors.ENDC}
      • {bcolors.BOLD}{bcolors.OKBLUE}ifconfig{bcolors.ENDC}
            """)
        elif cmd_name == "dps_config":
            print(f"""
        -- {bcolors.BOLD}DPS Configuration Settings{bcolors.ENDC} --

          {bcolors.BOLD}{bcolors.OKBLUE}dps_config {bcolors.ENDC}prompt (integer (0-9))
            """)
    else:
        print(f"""
     -- {bcolors.BOLD}Demon Pentest Shell{bcolors.ENDC} --

     {bcolors.BOLD}:: Built-In Commands ::{bcolors.ENDC}
      • {bcolors.BOLD}{bcolors.OKBLUE}help{bcolors.ENDC}: this cruft.
      • {bcolors.BOLD}{bcolors.OKBLUE}dps_stats{bcolors.ENDC}: all logging stats.
      • {bcolors.BOLD}{bcolors.OKBLUE}dps_uid_gen{bcolors.ENDC}: generate UIDs using "Firstname,Lastname" CSV file.
      • {bcolors.BOLD}{bcolors.OKBLUE}dps_wifi_mon{bcolors.ENDC}: Set Wi-Fi radio to RFMON.
      • {bcolors.BOLD}{bcolors.OKBLUE}dps_config{bcolors.ENDC}: Set prompt and shell options.
      • {bcolors.BOLD}{bcolors.OKBLUE}exit/quit{bcolors.ENDC}: return to terminal OS shell.

     {bcolors.BOLD}:: Keyboard Shortcuts ::{bcolors.ENDC}
      • {bcolors.BOLD}{bcolors.OKBLUE}CTRL+R{bcolors.ENDC}: Search command history.
      • {bcolors.BOLD}{bcolors.OKBLUE}CTRL+A{bcolors.ENDC}: Move cursor to beginning of line (similar to "HOME" key).
      • {bcolors.BOLD}{bcolors.OKBLUE}CTRL+P{bcolors.ENDC}: Place the previously ran command into the command line.
      • {bcolors.BOLD}{bcolors.OKBLUE}CTRL+B{bcolors.ENDC}: Move one character before cursor.
      • {bcolors.BOLD}{bcolors.OKBLUE}ALT+F{bcolors.ENDC}:  Move one character forward.
      • {bcolors.BOLD}{bcolors.OKBLUE}CTRL+C/D{bcolors.ENDC}: Exit the shell gracefully.
        """)

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
        else:
            OWD=os.getcwd() # store the directory that we are in for "-" purposes/historical
        if os.path.isdir(dir): # does it even exist?
            os.chdir(dir) # goto path
        else:
            print("PATH: "+bcolors.FAIL+'"'+dir+'"'+bcolors.ENDC+" does not exist.")
    else:
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd_delta])

###===========================================
## DPS CUSTOM BUILT-IN SHELL CMD METHODS:
###===========================================
def dps_update_config(args):
    global CONFIG # declare the global
    global CONFIG_FILENAME # config file name from global
    if len(args) > 1:
        if args[0] == "prompt": # set it in the config file:
            #try:
            print(f"{bcolors.OKBLUE}[+]{bcolors.ENDC} Adding "+str(args[1])+" as PRMPT_STYL in "+CONFIG_FILENAME)
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

###===========================================
## GENERAL METHODS FOR HANDLING THINGS:
###===========================================
def exit_gracefully(): # handle CTRL+C or CTRL+D, or quit, or exit gracefully:
        #ans = input(bcolors.FAIL+"\n[!] CTRL+C DETECTED\n[?] Do you wish to quit the Demon Pentest Shell (y/n)? "+bcolors.ENDC)
        ans = input(bcolors.FAIL+"\n[?]"+bcolors.ENDC+" Do you wish to quit the Demon Pentest Shell (y/n)? ")
        if ans == "y":
            print("[+] Quitting Demon Penetst Shell. File logged: "+LOG_FILENAME)
            sys.exit(1)

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
        elif path.startswith("./"):
            contents = os.listdir(os.getcwd())
        else:
            # This could be a command so try paths:
            contents=os.listdir(os.curdir) # current directory
            for item in contents: # if here, just return it
                if re.match(path,item):
                    return contents
            for path_entry in PATHS:
                try: # just learnt my first try/catch in Python - woohoo! :D
                    contents+=os.listdir(path_entry)
                    contents+=BUILTINS
                except:
                    pass
    return list(set(contents))

# Our custom completer function:
class DPSCompleter(Completer):
    def __init__(self, cli_menu):
        self.path_completer = PathCompleter()

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = list(map(lambda s: s.lower(), shlex.split(document.current_line)))
        except ValueError:
            pass
        else:

            if len(cmd_line)==2:
                if cmd_line[0] == "dps_config" and cmd_line[1] == "prompt":
                    options = ("0","1","2")
                    for opt in options:
                        yield Completion(opt,-len(word_before_cursor))
                    return
            if len(cmd_line): # at least 1 value
                current_str = cmd_line[len(cmd_line)-1]
                if cmd_line[0] == "dps_config":
                    options = ["prompt"]
                    yield Completion("prompt",-len(word_before_cursor))

                else:
                    if current_str == "~/":
                        options = list_folder(os.path.expanduser("~/"))
                    elif current_str == "./": # TODO
                        options = list_folder(os.getcwd())
                    else:
                        options = sorted(list_folder(current_str))
                    for opt in options:
                        if opt.startswith(current_str):
                            yield Completion(opt, -len(current_str))
                    return


class DPS:
    def set_message(self):
        self.path = os.getcwd()
        self.message = [
            ('class:username', UID),
            ('class:at','@'),
            ('class:host',HOSTNAME),
            ('class:colon',':'),
            ('class:path',self.path+"/"),
            ('class:dps',' (dps)'),
            ('class:pound',prompt_tail),
        ]

    def __init__(self):
        self.path = os.getcwd()
        if PRMPT_STYL == 2:
            self.style = Style.from_dict({
                # User input (default text).
                '':          '#ff0066',

                # Prompt.
                'username': '#884444',
                'at':       '#996633',
                'colon':    '#996633',
                'pound':    '#996633',
                'host':     '#00ffff bg:#444400',
                'path':     'ansicyan underline',
                'dps':      '#ffffff'
            })
        #####
        ### BLACK AND WHITE
        elif PRMPT_STYL == 1: # COFFEE
                self.style = Style.from_dict({
                    # User input (default text).
                    '':          '#fff',
                    # Prompt.
                    'username': 'italic #acacac',
                    'at':       'italic #aaaaaa',
                    'colon':    'italic #aaaaaa',
                    'pound':    '#aaaaaa',
                    'host':     'italic #c2c2c2',
                    'path':     'italic #ff321f',
                    'dps':      '#acacac'
                })
        else:
            self.style = Style.from_dict({
                # User input (default text).
                '':          '#ff0066',

                # Prompt.
                'username': '#884444',
                'at':       '#00aa00',
                'colon':    '#0000aa',
                'pound':    '#00aa00',
                'host':     '#00ffff bg:#444400',
                'path':     'ansicyan underline',
            })
        self.set_message()
        self.prompt_session = PromptSession(
            self.message,style=self.style,
            completer=DPSCompleter(self),
            complete_in_thread=True,
            complete_while_typing=False
        )

    def update_prompt(self):
        self.set_message()
        self.prompt_session.message = self.message

def shell(dps):
    try:
        last_string = dps.prompt_session.prompt()
        run_cmd(last_string)
        dps.update_prompt()
    except KeyboardInterrupt:
        exit_gracefully()
    except EOFError:
        exit_gracefully()


# standard boilerplate
if __name__ == "__main__":
    print(bcolors.BOLD+"\n *** Welcome to the Demon Pentest Shell ("+VERSION+")\n *** Type \"exit\" to return to standard shell.\n"+bcolors.ENDC)
    dps = DPS() # Prompt-toolkit class instance
    while True:
        shell(dps) #start the app
