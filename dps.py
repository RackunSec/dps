#!/usr/bin/env python3
# shell wrapper for superior logging
# logs as CSV with time,hostname,network:ip,who,command.
# requires Python 3+
#
# 2020 - Douglas Berdeaux
# version 1.2
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
LOG_FILENAME = os.path.expanduser("~")+"/.log_dps_history.csv"
HOSTNAME = socket.gethostname() # hostname for logging
UID = getpass.getuser()
REDIRECTION_PIPE = '_'
my_env = os.environ.copy()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

def log_cmd(cmd): # logging a command:
    with open(LOG_FILENAME,'a') as log_file:
        log_file.write(str(datetime.datetime.now())+","+HOSTNAME+","+str(NET_DEV)+","+UID+","+os.getcwd()+","+cmd+"\n")
    return 0

def run_cmd(cmd):

    cmd_delta = cmd
    cmd_delta = re.sub("~",os.path.expanduser("~"),cmd_delta)
    log_cmd(cmd_delta) # first, log the command.

    # Handle built-in commands:
    if (cmd == "exit" or cmd == "quit"):
        sys.exit()
        return 0
    if re.match("^ls",cmd):
        cmd_delta = re.sub("^ls","ls --color=auto",cmd)
    if re.match("^cd",cmd_delta):
        dir = re.sub('^cd\s+','',cmd_delta) # take off the path
        if (dir == "cd"): # go home
            dir = os.path.expanduser("~")
        os.chdir(dir) # goto path
        shell() # go back to prompt.
    else:
        #subprocess.Popen(cmd, env=my_env).wait() # kinda works?
        #subprocess.Popen(['/bin/bash', '-c', cmd],shell=True,env=my_env) # does not work?
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd_delta])
        shell()


def list_folder(path):
    """
    Lists folder contents
    """
    if path.startswith(os.path.sep):
        # absolute path
        basedir = os.path.dirname(path)
        contents = os.listdir(basedir)
        # add back the parent
        contents = [os.path.join(basedir, d) for d in contents]
    else:
        # relative path
        contents = os.listdir(os.curdir)
    return contents


def completer(text, state):
    """
    Our custom completer function
    """
    options = [x for x in list_folder(text) if x.startswith(text)]
    return options[state]

readline.set_completer(completer)
readline.parse_and_bind('tab: complete')
readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')


def shell():
    last_string = input(UID+bcolors.BOLD+"@"+bcolors.ENDC+HOSTNAME+bcolors.BOLD+"["+bcolors.ENDC+os.getcwd()+bcolors.BOLD+"]"+">> "+bcolors.ENDC)
    run_cmd(last_string)

shell() # start the app
