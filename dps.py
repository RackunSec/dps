#!/usr/bin/env python3
# shell wrapper for superior logging
# logs as CSV with time,hostname,network:ip,who,command.
# requires Python 3+
#
# 2020 - Douglas Berdeaux
#
import os # for the commands, of course. These will be passed ot the shell.
import subprocess # for piping commands
import sys # for exit
import re # regexps
from cmd2 import Cmd # The actual command-line lib
from cmd2 import style, fg, bg
import ifaddr # NIC info
import socket # for HOSTNAME
import getpass # for logging the username
import datetime # for logging the datetime

# constants:
ADAPTERS = ifaddr.get_adapters() # get network device info
NET_DEV = "" # store the network device
LOG_FILENAME = os.path.expanduser("~")+"/.log_dps_history.csv"
HOSTNAME = socket.gethostname() # hostname for logging
UID = getpass.getuser()

# Check if log file exists
if not os.path.exists(LOG_FILENAME):
    with open(LOG_FILENAME, 'w+') as new_log_file:
        new_log_file.write("Date,Hostname,Network,Who,Command\n")

for adapter in ADAPTERS: # loop over the adapters object
    if re.match("^e..[0-9]",adapter.nice_name): # looking for ethernet device here
        NET_DEV = adapter.nice_name+":"+str(adapter.ips[0].ip)
        break # we got what we need.

def log_cmd(cmd): # logging a command:
    #os.system("echo $(date),$(hostname),"+str(NET_DEV)+",$(whoami),"+cmd+" >> "+LOG_FILENAME)
    with open(LOG_FILENAME,'a') as log_file:
        log_file.write(str(datetime.datetime.now())+","+HOSTNAME+","+str(NET_DEV)+","+UID+","+cmd+"\n")
    return 0

def run_cmd(cmd):
    os.system(cmd)
    return 0

class REPL(Cmd): # Read Eval Print Loop

    prompt = "("+os.getcwd()+") dps> "

    def __init__(self):
        Cmd.__init__(self)
        super().__init__(use_ipython=True)
        # Intro Banner:
        self.intro = style(' *** Welcome to the Demon Pentest Shell\n *** hit CTRL+D to exit to standard shell.\n'+
            ' *** type cmd <command> to run basic shell commands.\n', bold=True)
        self.continuation_prompt="'-> "
        # Auto complete things, that don't do shit:
        self.allow_closing_quote = True
        self.allow_appended_space = True
        self.matches_delimited = False

    def do_cd(self,line):
        """[?] Change Directory. If space is in name, end with a double quote, \"."""
        log_cmd(line)
        nwd = re.sub(r'["]','',line)
        if (nwd == ""):
            nwd = os.path.expanduser('~')
        os.chdir(nwd)
        Cmd.async_update_prompt(self,"("+os.getcwd()+") dps> ")
        print("\n")
    complete_cd=Cmd.path_complete

    # This method is solely for tab autocompletion of file names:
    def do_x(self,line):
        log_cmd(line)
        run_cmd(line)
    complete_x = Cmd.path_complete

    def default(self,line):
        log_cmd(line.raw) # log it first:
        run_cmd(line.raw) # run it.
    # complete_default = Cmd.path_complete # doesn't work, unfortunately.

    def do_exit(self,line):
        """[?] Exit the Demon Pentest Shell."""
        sys.exit()

if __name__ == '__main__':
    app = REPL()
    app.cmdloop()
