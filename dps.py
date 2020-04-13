#!/usr/bin/env python3
# shell wrapper for superior logging
# logs as CSV with time,hostname,network:ip,who,command.
# requires Python 3+
#
# 2020 - Douglas Berdeaux
#
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
    if re.match("^cd\s",cmd):
        dir = re.sub('^cd\s+','',cmd)
        os.chdir(dir)
    else:
        os.system(cmd)
    return 0

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
