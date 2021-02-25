#!/usr/bin/env python3
# The Demon (DEMON LINUX) Penetration Testing Shell
# Custom shell for superior logging during a penetration test.
# logs as CSV with time,hostname,network:ip,who,command in the ~/.dps/ directory
# requires Python 3+
#
# 2021 - Douglas Berdeaux, Matthew Creel
# (dps) dberdeaux@schneiderdowns.com
#
### IMPORT LIBRARIES:
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
from prompt_toolkit.output.color_depth import ColorDepth # colors for prompt
import git # for dps_update command

### SESSION AND USER INFO:
class Session:
    def __init__(self):
        self.ADAPTERS = ifaddr.get_adapters() # get network device info
        self.NET_DEV = "" # store the network device
        self.HOSTNAME = socket.gethostname() # hostname for logging
        self.UID = getpass.getuser() # Get the username
        self.REDIRECTION_PIPE = '_' # TODO not needed?
        self.VERSION = "v1.2.25-gamma-mega" # update this each time we push to the repo (version (year),(mo),(day),(revision))
        self.LOG_DAY = datetime.datetime.today().strftime('%Y-%m-%d') # get he date for logging purposes
        self.LOG_FILENAME = os.path.expanduser("~")+"/.dps/logs/"+self.LOG_DAY+"_dps_log.csv" # the log file is based on the date
        self.CONFIG_FILENAME = os.path.expanduser("~")+"/.dps/config/dps.ini" # config (init) file name
        self.CONFIG = configparser.ConfigParser() # config object
        self.OWD=os.getcwd() # historical purposes
        # Add all built-in commands here so they populate in the tab-autocompler:
        self.BUILTINS=['dps_stats','dps_uid_gen','dps_wifi_mon','dps_config','foreach','dps_alias','dps_update']
        self.VARIABLES = {} # all user-defined variables.
        self.PRMPT_STYL=0 # Prompt style setting
        self.prompt_tail = "# " if self.UID == "root" else "> " # diff root prompt
        self.ALIASES = {} # all user-defined aliases
        self.DPSBINPATH = "" # binary path for this (or installaed) dps.py executable
        self.CUSTPATHS = [] # custom paths in dps.ini file, dedpuled and link-read
        # Bash built-ins:
        self.BASHBI=['bg', 'bind', 'break', 'builtin', 'case', 'cd', 'command', 'compgen', 'complete', 'continue', 'declare',
            'dirs', 'disown', 'echo', 'enable', 'eval', 'exec', 'exit', 'export', 'fc', 'fg', 'getopts', 'hash', 'if', 'jobs', 'kill',
            'let', 'local', 'logout', 'popd', 'printf', 'pushd', 'pwd', 'read', 'readonly', 'return', 'set', 'shift', 'shopt', 'source',
            'suspend', 'test', 'times', 'trap', 'type', 'typeset', 'ulimit', 'umask', 'unalias', 'unset', 'until', 'wait','while']
        self.IGNOREDUPES = ['ls','which','pwd','cwd','grep','egrep','sed','awk',]
    def init_config(self): # initialize the configuration:
        if not os.path.exists(os.path.join(os.path.expanduser("~"),".dps")): # create the directory if it does not exist
            os.mkdir(os.path.join(os.path.expanduser("~"),".dps")) # mkdir
            os.mkdir(os.path.join(os.path.expanduser("~"),".dps/config")) # mkdir
            os.mkdir(os.path.join(os.path.expanduser("~"),".dps/logs")) # mkdir
        # Set up the log file itself:
        if not os.path.exists(self.LOG_FILENAME):
            with open(self.LOG_FILENAME,'a') as log_file:
                log_file.write("When,Host,Network,Who,Where,What\n")
        # Set up the config file/pull values:
        if not os.path.exists(self.CONFIG_FILENAME):
            # Add the file
            with open(self.CONFIG_FILENAME,'a') as config_file:
                ### ADD ALL CONFIG STUFF HERE:
                ## ADD STYLE:
                config_file.write("[Style]\n")
                config_file.write("PRMPT_STYL = 5\n")
                ## ADD PATHS:
                config_file.write("\n[Paths]\n")
                config_file.write("MYPATHS = /usr/bin:/bin:/sbin:/usr/local/bin:/usr/local/sbin\n")
                config_file.write("DPS_bin_path=/cyberpunk/shells/dps/\n")
                config_file.write("\n[Aliases]\n")
                config_file.write("grep = grep --color\n")
                config_file.write("egrep = egrep --color\n")
                config_file.write("ls = ls --color=auto\n")
            print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['OKGREEN']} Configuration file generated. Please restart shell.{prompt_ui.bcolors['ENDC']}")
            sys.exit(0)
        else:
            # Config file exists, grab the values using configparser:
            self.CONFIG.read(self.CONFIG_FILENAME) # read the file
            self.CONFIG.sections() # get all sections of the config
            # Check for a prompt-style or die:

            if 'Paths' in self.CONFIG:
                self.PATHS = self.CONFIG['Paths']['MYPATHS'].split(":") # ARRAY
                # check if symlinks in paths. Also, remove dpues:
                for path in self.PATHS:
                    #print(f"Trying: {path}")
                    if path not in self.CUSTPATHS:
                        if os.path.islink(path): # was it a symlink?
                            if "/"+os.readlink(path) not in self.CUSTPATHS:
                                self.CUSTPATHS.append("/"+os.readlink(path))
                        else:
                            self.CUSTPATHS.append(path)
                self.PATHS = self.CUSTPATHS # overwrite it
                self.DPSBINPATH = self.CONFIG['Paths']['DPS_bin_path']
                # check if valid
                if os.path.isdir(self.DPSBINPATH):
                    # check all paths and issue warning:
                    for path in self.PATHS:
                        if not os.path.isdir(path):
                            print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['FAIL']} FATAL: Path defined ({path}) in [Paths] section of dps.ini file does not exist! {prompt_ui.bcolors['ENDC']}")
                            sys.exit(1)
                else:
                    print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['FAIL']} Error in config file: Ensure 'DPS_bin_path' value is a valid path in [Paths] of "+self.CONFIG_FILENAME+f"{prompt_ui.bcolors['ENDC']}")
                    sys.exit() # die
            else:
                print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['FAIL']} Error in config file: Add [Paths] section to "+self.CONFIG_FILENAME+f"{prompt_ui.bcolors['ENDC']}")
                sys.exit() # die

            if 'Style' in self.CONFIG:
                session.PRMPT_STYL = int(self.CONFIG['Style']['PRMPT_STYL']) # grab the value of the style
            else:
                print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['FAIL']}{prompt_ui.bcolors['ENDC']} Error in config file: Add [Style] section to "+self.CONFIG_FILENAME)
                sys.exit() # die

            # check for aliases:
            if 'Aliases' in self.CONFIG:
                self.ALIASES = self.CONFIG['Aliases']

### UI STUFF:
class Prompt_UI:
    bcolors = {
        'OKGREEN' : '\033[3m\033[92m',
        'FAIL' : '\033[3m\033[91m',
        'ENDC' : '\033[0m',
        'BOLD' : '\033[1m',
        'YELL' : '\033[33m',
        'ITAL' : '\033[3m',
        'BLUE' : '\033[34m'
    }
    dps_themes = {
        0 : 'DPS',
        1 : 'PIRATE',
        2 : 'BONEYARD',
        3 : '1980S',
        5 : 'Nouveau'
    }
prompt_ui = Prompt_UI() # Object with UI data
session = Session() # Object with Session data and user config
session.init_config() # initialize the configuration.

###===========================================
## PRELIMINARY FILE/DESCRIPTOR WORK:
###===========================================


def error(msg,cmd):
    print(f"{prompt_ui.bcolors['BOLD']}[?]{prompt_ui.bcolors['FAIL']}{prompt_ui.bcolors['ENDC']}{prompt_ui.bcolors['FAIL']} ¬_¬ wut? -- "+msg+f"{prompt_ui.bcolors['ENDC']}")
    if cmd != "":
        help(cmd) # show the Help dialog from the listings above

# Get the adapter and IP address:
def get_net_info():
    for adapter in session.ADAPTERS: # loop through adapters
        if re.match("^e..[0-9]+",adapter.nice_name):
            try:
                session.NET_DEV = adapter.nice_name+":"+adapter.ips[0].ip
            except:
                error("No network address is ready. Please get a network address before continuing for logging purposes.","")
                help("dps_config") # show help for config.
                session.NET_DEV = "0.0.0.0" # no address?
get_net_info()

def log_cmd(cmd): # logging a command to the log file:
    with open(session.LOG_FILENAME,'a') as log_file:
        log_file.write(str(datetime.datetime.now())+","+session.HOSTNAME+","+str(session.NET_DEV)+","+session.UID+","+os.getcwd()+","+cmd+"\n")
    return 0

###===========================================
## CUSTOM HELP DIALOGS:
###===========================================
def help(cmd_name):
    if cmd_name != "":
        if cmd_name == "dps_uid_gen":
                print(f"""
 -- {prompt_ui.bcolors['BOLD']}DPS UID Generator Usage{prompt_ui.bcolors['ENDC']} --

  {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}dps_uid_gen {prompt_ui.bcolors['ENDC']}(format specifier) (csv file)

  :: {prompt_ui.bcolors['BOLD']}Format Specifiers{prompt_ui.bcolors['ENDC']} ::
   • {prompt_ui.bcolors['BOLD']}%F{prompt_ui.bcolors['ENDC']}: First Name.
   • {prompt_ui.bcolors['BOLD']}%f{prompt_ui.bcolors['ENDC']}: First Initial.
   • {prompt_ui.bcolors['BOLD']}%L{prompt_ui.bcolors['ENDC']}: Last Name.
   • {prompt_ui.bcolors['BOLD']}%l{prompt_ui.bcolors['ENDC']}: Last Initial.

  :: {prompt_ui.bcolors['BOLD']}Notes:{prompt_ui.bcolors['BOLD']} ::
  You can add anything else you wish, such as,
   e.g: %f.%L123@client.org
   result: j.doe123@client.org
                """)
        elif cmd_name == "def":
            print(f"""
 -- {prompt_ui.bcolors['BOLD']}Defining Variables{prompt_ui.bcolors['ENDC']} --

   :: {prompt_ui.bcolors['BOLD']}Syntax{prompt_ui.bcolors['ENDC']} ::
    • {prompt_ui.bcolors['BOLD']}def (var name): (value){prompt_ui.bcolors['ENDC']}
            """
            )
        elif cmd_name == "dps_alias":
            print(f"""
 -- {prompt_ui.bcolors['BOLD']}List aliases defined in ~/.dps/dps.ini's [ALIASES] section{prompt_ui.bcolors['ENDC']} --

   :: {prompt_ui.bcolors['BOLD']}Syntax{prompt_ui.bcolors['ENDC']} ::
    • {prompt_ui.bcolors['BOLD']}dps_alias{prompt_ui.bcolors['ENDC']}
            """
            )
        elif cmd_name == "foreach":
                print(f"""
 -- {prompt_ui.bcolors['BOLD']}DPS foreach(){prompt_ui.bcolors['ENDC']} --

  {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}foreach() {prompt_ui.bcolors['ENDC']}Loop function.

  :: {prompt_ui.bcolors['BOLD']} Syntax Examples{prompt_ui.bcolors['ENDC']} ::
   • {prompt_ui.bcolors['BOLD']}foreach({prompt_ui.bcolors['ENDC']}/path/to/file.txt{prompt_ui.bcolors['BOLD']}){prompt_ui.bcolors['ENDC']} as line: echo $line
   • {prompt_ui.bcolors['BOLD']}foreach({prompt_ui.bcolors['ENDC']}m..n{prompt_ui.bcolors['BOLD']}){prompt_ui.bcolors['ENDC']} as int: nmap 192.168.1.$int
                """)
        elif cmd_name == "dps_wifi_mon":
            print(f"""
 -- {prompt_ui.bcolors['BOLD']}DPS Wi-Fi Monitor Mode{prompt_ui.bcolors['ENDC']} --

  {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}dps_wifi_mon {prompt_ui.bcolors['ENDC']}(wi-fi device)

  :: {prompt_ui.bcolors['BOLD']}Requirements{prompt_ui.bcolors['ENDC']} ::
   • {prompt_ui.bcolors['BOLD']}iw{prompt_ui.bcolors['ENDC']} - used to set up the Wi-Fi adapter.
   • {prompt_ui.bcolors['BOLD']}airmon-ng{prompt_ui.bcolors['ENDC']} - Used to kill processes.
   • {prompt_ui.bcolors['BOLD']}ifconfig{prompt_ui.bcolors['ENDC']} - used to turn on and off the adapter.
            """)
        elif cmd_name == "dps_config":
            print(f"""
 -- {prompt_ui.bcolors['BOLD']}DPS Configuration Settings{prompt_ui.bcolors['ENDC']} --

  {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}dps_config {prompt_ui.bcolors['ENDC']}(Options)

  :: {prompt_ui.bcolors['BOLD']}Options{prompt_ui.bcolors['ENDC']} ::
   • {prompt_ui.bcolors['BOLD']}prompt (0-9){prompt_ui.bcolors['ENDC']} - Set the prompt style.
   • {prompt_ui.bcolors['BOLD']}--show{prompt_ui.bcolors['ENDC']} - Show all config options from the dps.ini file.
   • {prompt_ui.bcolors['BOLD']}--update-net{prompt_ui.bcolors['ENDC']} - Get an IP address.
            """)
    else:
            print(f"""
 -- {prompt_ui.bcolors['BOLD']}Demon Pentest Shell{prompt_ui.bcolors['ENDC']} --

 {prompt_ui.bcolors['BOLD']}:: Built-In Commands ::{prompt_ui.bcolors['ENDC']}
  • {prompt_ui.bcolors['BOLD']}help{prompt_ui.bcolors['ENDC']}: this cruft.
  • {prompt_ui.bcolors['BOLD']}dps_stats{prompt_ui.bcolors['ENDC']}: all logging stats.
  • {prompt_ui.bcolors['BOLD']}dps_alias{prompt_ui.bcolors['ENDC']}: show all aliases defined in dps.ini's [ALIASES] section.
  • {prompt_ui.bcolors['BOLD']}dps_update{prompt_ui.bcolors['ENDC']}: update DPS (using GitPython) in DPS_bin_path as defined in dps.ini's [Paths] section.
  • {prompt_ui.bcolors['BOLD']}dps_uid_gen{prompt_ui.bcolors['ENDC']}: generate UIDs using "Firstname,Lastname" CSV file.
  • {prompt_ui.bcolors['BOLD']}dps_wifi_mon{prompt_ui.bcolors['ENDC']}: Set Wi-Fi radio to RFMON.
  • {prompt_ui.bcolors['BOLD']}dps_config{prompt_ui.bcolors['ENDC']}: Set prompt and shell options.
  • {prompt_ui.bcolors['BOLD']}exit/quit{prompt_ui.bcolors['ENDC']}: return to terminal OS shell.

 {prompt_ui.bcolors['BOLD']}:: Programming Logic ::{prompt_ui.bcolors['ENDC']}
  • {prompt_ui.bcolors['BOLD']}foreach(){prompt_ui.bcolors['ENDC']}: perform for loop on file contents or integer range.

 {prompt_ui.bcolors['BOLD']}:: Keyboard Shortcuts ::{prompt_ui.bcolors['ENDC']}
  • {prompt_ui.bcolors['BOLD']}CTRL+R{prompt_ui.bcolors['ENDC']}: Search command history.
  • {prompt_ui.bcolors['BOLD']}CTRL+A{prompt_ui.bcolors['ENDC']}: Move cursor to beginning of line (similar to "HOME" key).
  • {prompt_ui.bcolors['BOLD']}CTRL+P{prompt_ui.bcolors['ENDC']}: Place the previously ran command into the command line.
  • {prompt_ui.bcolors['BOLD']}CTRL+B{prompt_ui.bcolors['ENDC']}: Move one character before cursor.
  • {prompt_ui.bcolors['BOLD']}ALT+F{prompt_ui.bcolors['ENDC']}:  Move one character forward.
  • {prompt_ui.bcolors['BOLD']}CTRL+C{prompt_ui.bcolors['ENDC']}: Kill current process.
            """)

###===========================================
## COMMAND HOOKS:
###===========================================
def hook_cmd(cmd): # run a command. We capture a few and handle them, like "exit","quit","cd","sudo",etc:
    cmd_root = re.sub("\s+.*","",cmd) # just the first word of the command (no args)
    # check our user-defined aliases:
    if len(session.ALIASES) > 0:
        for alias in session.ALIASES:
            cmd = re.sub(alias,session.ALIASES[alias],cmd) # all occurrences

    cmd_delta = cmd # the delta will be mangled user input as we see later:
    cmd_delta = re.sub("~",os.path.expanduser("~"),cmd_delta)
    cmd_delta = re.sub("^\s+","",cmd_delta) # remove any prepended spaces

    # interpolate any variables:
    if re.match(".*\{[^\}]+\}.*",cmd_delta):
        # I chose a very unique variablename here on purposes to not collide.
        var123_0x031337 = re.sub(r"^[^\{]+{([^\}]+)}.*$","\\1",cmd_delta) # TODO interpolate multiple times! (use a while loop) (wait, can you do global replace?)
        var_re = re.compile("{"+var123_0x031337+"}")
        if session.VARIABLES.get(var123_0x031337): # it exists
            cmd_delta = re.sub(var_re,session.VARIABLES[var123_0x031337],cmd_delta)
        else:
            error(f"Variable declared not yet defined: {var123_0x031337}","def")
            return

    log_cmd(cmd_delta) # first, log the command.
    # Handle built-in commands:
    if cmd_delta == "exit" or cmd_delta == "quit":
        exit_gracefully()

    ### Programming logic:
    elif cmd_delta.startswith("foreach"): # foreach (file.txt) as line: echo line
        foreach(cmd_delta) # See "Built-In Programming Logic" section below for definition of method.
    elif cmd_delta.startswith("dps_wifi_mon"):
        args = cmd_delta.split()
        if len(args)>1:
            dps_wifi_mon(args[1]) # should be the device
        else:
            error("Not enough arguments.","dps_wifi_mon")
            return
    elif cmd_delta.startswith("def "): # def var: val
        args = re.sub("^def\s+","",cmd_delta) # grab the arguments
        var = re.sub(":.*","",args)
        val = re.sub("[^:]+:(\s+)?","",args)
        if var != "" and val != "":
            print(f"{prompt_ui.bcolors['BOLD']}[i]{prompt_ui.bcolors['ENDC']} Assigning {prompt_ui.bcolors['BOLD']}{prompt_ui.bcolors['ITAL']}{val}{prompt_ui.bcolors['ENDC']} to {prompt_ui.bcolors['BOLD']}{prompt_ui.bcolors['ITAL']}{var}{prompt_ui.bcolors['ENDC']}") # DEBUG
            session.VARIABLES[var]=val # set it.
        else:
            error("Incorrect syntax for defining a value.","def")
            return
    elif re.match("^\s?sudo",cmd_delta): # for sudo, we will need the command's full path:
        sudo_regexp = re.compile("sudo ([^ ]+)")
        cmd_delta=re.sub(sudo_regexp,'sudo $(which \\1)',cmd_delta)
        run_cmd(cmd_delta)
        return
    elif cmd_delta.startswith("dps_uid_gen"):
        args = cmd_delta.split()
        if len(args)==3:
            dps_uid_gen(args[1],args[2]) # should be "format specifier, filename"
        else:
            error("Not enough arguments.","dps_uid_gen")
            return
    elif(cmd_delta=="dps_stats"):
        dps_stats()
    elif(cmd_delta=="dps_update"):
        dps_update()
    elif(cmd_delta=="dps_alias"):
        dps_alias()
    elif(cmd_delta.startswith("dps_config")):
        args = re.sub("dps_config","",cmd_delta).split() # make an array
        if len(args) > 0:
            dps_config(args)
        else:
            error("Not enough arguments.","dps_config")
    elif(cmd_delta.startswith("help")):
        args = cmd_delta.split()
        if(len(args)>1):
            help(args[1])
        else:
            help("")
    ###---------
    ## VERSION @override:
    ###---------
    elif(cmd_delta=="version"):
        print(f"{prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['OKGREEN']}Demon Pentest Shell - "+session.VERSION+"{prompt_ui.bcolors['ENDC']}")
    ###---------
    ### WARN Leaving DPS:
    ###---------
    elif(cmd_delta=="bash"):
        print(f"{prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}[i] WARNING - Leaving DPS for Bash shell (CTRL+D to return to DPS){prompt_ui.bcolors['ENDC']}")
        run_cmd(cmd_delta)

    ###---------
    ## LS @override:
    ###---------
    elif(re.match("^ls",cmd_delta)):
        cmd_delta = re.sub("^ls","ls --color=auto",cmd)
        run_cmd(cmd_delta)
    ###---------
    ## CLEAR @override:
    ###---------
    elif(cmd_delta == "clear"):
        print("\033c", end="") # we clear our own terminal :)
    ###---------
    ## CD @Override:
    ###---------
    elif(cmd_delta.startswith("cd")):
        global OWD # declare that we want to use this.
        if len(cmd_delta.split())>1:
            where_to = cmd_delta.split()[1]
        else:
            os.chdir(os.path.expanduser("~/"))
            return
        if where_to == "-":
            BOWD = OWD # back it up
            OWD = os.getcwd()
            os.chdir(BOWD)
            return
        else:
            OWD = os.getcwd()
        # Finally, we change directory:
        if os.path.exists(where_to):
            os.chdir(where_to)
            return
        else:
            error("Path does not exist: "+where_to,"")
    else: # Any OTHER command:
        run_cmd(cmd_delta)
    return

###===========================================
## Actually RUN the commands:
###===========================================
def run_cmd(cmd):
    if cmd=="":
        return
    if cmd.startswith("./") or cmd.startswith("/") or re.match("^[^/]+/",cmd):
        # user specified a path, just try it: TODO ensure binary in path before executing.
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
        return
    else:
        # get the actual binary called:
        bin = cmd.split()[0] # get the first arg which is the command
        # Is the binary in any of our defined paths?
        # get path contents:
        bin_paths = [] # could be more than one instance in paths (python envs, etc)
        all_paths = session.PATHS # this could change since we also have cwd (.)
        if os.getcwd() not in all_paths:
            all_paths.append(os.getcwd())
        for path in all_paths:
            if bin in os.listdir(path):
                bin_paths.append(path+"/"+bin)
        if len(bin_paths)>1:
            print(f"{prompt_ui.bcolors['YELL']}[?] WARNING: binary file ({bin}) discovered in multiple paths:\n--------------------------------{prompt_ui.bcolors['ENDC']}")
            count = 0;
            for path in bin_paths:
                print(f"{prompt_ui.bcolors['BOLD']}[{prompt_ui.bcolors['OKGREEN']}{count}{prompt_ui.bcolors['ENDC']}{prompt_ui.bcolors['BOLD']}]{prompt_ui.bcolors['ENDC']} {prompt_ui.bcolors['OKGREEN']}{path}{prompt_ui.bcolors['ENDC']}")
                count+=1
            print(f"\n{prompt_ui.bcolors['BOLD']}[?]{prompt_ui.bcolors['ENDC']} Please choose one:",end=" ")
            ans=int(input())
            try:
                if bin_paths[ans]:
                    #print(f"You chose: {ans} which is {bin_paths[ans]}")
                    subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
                    return
            except:
                print(f"{prompt_ui.bcolors['FAIL']} INDEX: {str(ans)} out of range of list provided to you.{prompt_ui.bcolors['ENDC']}")
                return
        elif len(bin_paths)==1: # we found the command (binary):
            subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
            return
        else:
            print(f"{prompt_ui.bcolors['FAIL']}[!] Binary: {bin} not found in paths.\n  Check your [Paths] within the DPS configuration file.")
            return
    return

###===========================================
## Built-In Programming Logic:
###===========================================
def foreach(cmd_delta): # FOREACH
    cmd_args = re.sub("^foreach(\s+)?","",cmd_delta)
    if cmd_args == "":
        help("foreach")
    else:
        object = re.sub(".*\(([^\)]+)\).*","\\1",cmd_args)
        if object != "":
            # now get the variable:
            var = re.sub(".*as\s+([^:]+).*","\\1",cmd_args)
            cmd_do = re.sub("[^:]+:","",cmd_args)
            if var == "":
                error("Programming logic syntax error. Please check the documentation.","")
            elif var not in cmd_do:
                # the wrong varname was used in the do{} portion:
                error("Programming logic syntax error. Did you mean to use: $"+var+"?","")
            else:
                if re.search("[0-9]+\.\.[0-9]+",object):
                    # we have integers:
                    int_start = int(re.sub("^([0-9]+)\..*","\\1",object))
                    int_end = int(re.sub(".*\.\.([0-9]+)$","\\1",object))+1
                    int_range = range(int_start,int_end)
                    # pull out what to do with the entry:
                    do = re.sub("^[^:]+:","",cmd_delta)
                    for i in int_range: # 0..9
                        do_re = re.compile("\$"+var)
                        do_cmd = re.sub(do_re,str(i),do)
                        #print(f"[pl] cmd: "+do_cmd+" var: "+var)
                        run_cmd(do_cmd)
                elif os.path.exists(object): # this is a file
                    # pull out what to do with the entry:
                    do = re.sub("^[^:]+:","",cmd_delta)
                    with open(object) as object_file:
                        for entry in object_file:
                            # replace entry with $var in do:
                            do_re = re.compile("\$"+var)
                            do_cmd = re.sub(do_re,entry.strip(),do)
                            run_cmd(do_cmd)
                else:
                    error("Could not access object: "+object,"")
        else:
            error("Programming logic syntax error. Please check the documentation.","")

###===========================================
## DPS CUSTOM BUILT-IN SHELL CMD METHODS:
###===========================================
def dps_update():
    # pull an updated version from GitHUB and rewrite the specified path in [Paths]['DPS_bin_path'] from the ini file:
    try:
        g = git.cmd.Git(session.DPSBINPATH)
        g.stash('save')
        g.pull(force=True)
        print(f"\n{prompt_ui.bcolors['BOLD']}[i]{prompt_ui.bcolors['ENDC']} {prompt_ui.bcolors['OKGREEN']}Successfully pulled changes to local repository: {session.DPSBINPATH} {prompt_ui.bcolors['ENDC']}\n")
    except:
        print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['FAIL']} Something went wrong when trying to perform git operations. {prompt_ui.bcolors['ENDC']}")

def dps_update_config(args):
    if len(args) > 1:
        if args[0] == "prompt": # set it in the config file:
            #try:
            print(f"{prompt_ui.bcolors['OKGREEN']}[i]{prompt_ui.bcolors['ENDC']} Adding "+str(args[1])+" as PRMPT_STYL in "+session.CONFIG_FILENAME)
            session.CONFIG.set('Style','PRMPT_STYL',args[1]) # TODO int() ?
            with open(session.CONFIG_FILENAME, 'w') as config_file:
                session.CONFIG.write(config_file)

def dps_alias():
    print(prompt_ui.bcolors['BOLD']+"\n :: DPS.ini Defined [ALIASES] :: "+prompt_ui.bcolors['ENDC'])
    for alias in session.ALIASES:
        print(f"  • Alias found for {prompt_ui.bcolors['OKGREEN']}{alias}{prompt_ui.bcolors['ENDC']} as '{prompt_ui.bcolors['OKGREEN']}{session.ALIASES[alias]}{prompt_ui.bcolors['ENDC']}'")
    print("")
    return
def dps_config(args): # configure the shell
    session.PRMPT_STYL # this is the prompt color setting
    if args[0] == "prompt" and args[1] != "":
        session.PRMPT_STYL = int(args[1])
        # Now set it for session / preference in the dps.ini file:
        dps_update_config(args)
    elif args[0] == "--show":
        print(f"{prompt_ui.bcolors['BOLD']}[i]{prompt_ui.bcolors['ENDC']} Current DPS Prompt Theme: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+prompt_ui.dps_themes[session.PRMPT_STYL]+f"{prompt_ui.bcolors['ENDC'] }")
    elif args[0] == "--update-net":
        print(f"{prompt_ui.bcolors['BOLD']}{prompt_ui.bcolors['OKGREEN']}[i] Obtaining IP address via dhclient... {prompt_ui.bcolors['ENDC']}")
        subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", "dhclient -v"])
        get_net_info(session.NET_DEV)
        return
    else:
        print("Usage: dps_config prompt [0-9] for new prompt.")

def dps_wifi_mon(dev): # set an AC device into monitor mode using iw
    print("Set device "+dev+" into RFMON monitor mode.")
# stats for shell logging
def dps_stats():
    file_count = len(os.listdir(os.path.expanduser("~/.dps/logs/")))
    print(prompt_ui.bcolors['BOLD']+"\n :: DPS Logging Stats :: "+prompt_ui.bcolors['ENDC'])
    print(f"  • Log file count: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+str(file_count)+prompt_ui.bcolors['ENDC'])
    print(f"  • Log file location: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+os.path.expanduser("~/.dps/logs/")+prompt_ui.bcolors['ENDC'])
    line_count = int(0) # declare this
    for file in os.listdir(os.path.expanduser("~/.dps/logs/")):
        line_count += len(open(os.path.expanduser("~/.dps/logs/")+file).readlines())
    print(f"  • Total entries: {prompt_ui.bcolors['ITAL']}{prompt_ui.bcolors['YELL']}"+str(line_count)+prompt_ui.bcolors['ENDC']+"\n")

# USER ID FROM CSV GENERATOR:
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
        print(f"{prompt_ui.bcolors['BOLD']}[!]"+prompt_ui.bcolors['FAIL']+" Could not open file: "+csv_file+" for reading."+prompt_ui.bcolors['ENDC'])

###===========================================
## GENERAL METHODS FOR HANDLING THINGS:
###===========================================
def exit_gracefully(): # handle CTRL+C or CTRL+D, or quit, or exit gracefully:
    sys.exit(0);

###=======================================
## OUR CUSTOM COMPLETER: (a nightmare)
###=======================================
class DPSCompleter(Completer):
    def __init__(self, cli_menu):
        self.path_completer = PathCompleter()
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = document.current_line.split() # make an array
        except ValueError:
            pass
        else: # code runs ONLY if no exceptions occurred.
            if len(cmd_line)==2:
                if cmd_line[0] == "dps_config" and cmd_line[1] == "prompt":
                    options = ("0","1","2","3")
                    for opt in options:
                        yield Completion(opt,-len(word_before_cursor))
                    return
            if document.get_word_before_cursor() == "": # trying to cat a file in the cwd perhaps?
                options = os.listdir(os.getcwd())
                for opt in options:
                    yield Completion(opt, 0,style='italic')
                return

            if len(cmd_line): # at least 1 value
                current_str = cmd_line[len(cmd_line)-1]
                if current_str.startswith("foreach"):
                    path=re.sub("foreach.","",current_str)
                    if path.startswith("/"):
                        path_to=re.sub("[^/]+$","",path) # chop off end text
                        match = re.sub(".*/","",path) # greedily remove path
                        options = os.listdir(path_to)
                        for opt in options:
                            if opt.startswith(match):
                                yield Completion("foreach("+path_to+opt,-len(current_str),style='italic')
                        return
                    else:
                        return
                    return
                if cmd_line[0] == "dps_config":
                    options = ["prompt","--show","--update-net"]
                    for opt in options:
                        yield Completion(opt,-len(word_before_cursor))
                else:
                    # TAB Autocompleting arguments? :
                    if len(cmd_line) > 1:
                        if "/" in cmd_line[-1]: # directory traversal?
                            if re.match("^[A-Za-z0-9\.]",cmd_line[-1]) and cmd_line[-1].endswith("/"): # e.g.: cd Documents/{TAB TAB}
                                dir = os.getcwd()+"/"+cmd_line[-1]
                                options = os.listdir(dir)
                                for opt in options:
                                    opt2 = dir+opt
                                    if os.path.isdir(opt2):
                                        opt2 += "/" # this is a directory
                                    yield Completion(opt2, -len(current_str),style='italic')
                                return
                            elif re.match("^[A-Za-z0-9\.]",cmd_line[-1]) and (not cmd_line[-1].endswith("/")): # e.g.: cd Documents/Te{TAB TAB}
                                tab_com = current_str.split("/")[-1]
                                dir = os.getcwd()+"/"+re.sub("[^/]+$","",current_str)
                                options = os.listdir(dir)
                                for opt in options:
                                    if opt.startswith(tab_com):
                                        yield Completion(dir+opt, -len(current_str),style='italic')
                                return
                            elif re.match("^/",cmd_line[-1]):
                                # get path:
                                path_to = re.sub("[^/]+$","",cmd_line[-1])
                                what_try = cmd_line[-1].split("/")[-1]
                                options = os.listdir(path_to)
                                for opt in options:
                                    if opt.startswith(what_try):
                                        if(os.path.isdir(path_to+opt+"/")): # is a directory - append a slash to "keep going" with TAB:
                                            yield Completion(path_to+opt+"/", -len(current_str),style='italic')
                                        else: # not a directory:
                                            yield Completion(path_to+opt, -len(current_str),style='italic')
                                return

                        # Get the path off of the document.current_line object:
                        current_str = cmd_line[len(cmd_line)-1]
                        path_to = re.sub("(.*)/[^/]+$","\\1/",cmd_line[1])
                        object = cmd_line[-1].split("/")[-1] # last element, of course.

                        if path_to.startswith("~/"):
                            dir = os.path.expanduser(path_to)
                        elif path_to.startswith("/"): # full path:
                            dir = path_to
                        else:
                            dir = os.getcwd()

                        # now that we have defined "dir" let's get the contents:
                        options = list(set(os.listdir(dir))) # this will only sshow unique values.
                        for opt in options:
                            auto_path = "" # use this as starting point.
                            if opt.startswith(object):
                                if path_to.startswith("~/"): # expand it if we have ~ shortcut.
                                    path_to = os.path.expanduser(path_to) # path_to now expanded.
                                if os.path.isdir(path_to+opt): # if it's a dir, append a fwd shlash.
                                    auto_path = path_to+opt+"/" # fwd slash appended.
                                else:
                                    if path_to.startswith("./") or path_to.startswith("/") or path_to.startswith("~/"):
                                        auto_path = path_to+opt # add the entire path
                                    else:
                                        auto_path = opt
                                yield Completion(auto_path, -len(current_str),style='italic')
                        return
                    # Run from cwd? :
                    elif cmd_line[0].startswith("./"):
                        cmd = re.sub("./","",cmd_line[0])
                        options = os.listdir(os.getcwd())
                        for opt in options:
                            if opt.startswith(cmd): # that after the ./
                                yield Completion("./"+opt, -len(current_str),style='italic')
                        return
                    # Run from PATH:
                    else: # just pull in what we need - not everything:
                        options = session.BUILTINS # make sure we get the built-in DPS commands
                        options += session.BASHBI # append Bash built-ins as they don't live in $PATH
                        for path in session.PATHS:
                            for binary in os.listdir(path):
                                if binary.startswith(current_str):
                                    if binary not in options:
                                        options.append(binary)
                        for opt in options:
                            #print(opt)
                            if opt.startswith(current_str): # weeds out dps_ built-ins
                                yield Completion(opt, -len(current_str),style='italic')
                        return

###=======================================
## OUR CUSTOM SHELL DEFINITION:
###=======================================
class DPS:
    def set_message(self):
        # This defines the prompt content:
        self.path = os.getcwd()+"/"


        if session.PRMPT_STYL == 0: # DEFAULT SHELL
            self.message = [
                ('class:username', session.UID),
                ('class:at','@'),
                ('class:host',session.HOSTNAME),
                ('class:colon',':'),
                ('class:path',self.path),
                ('class:dps','(dps)'),
                ('class:pound',session.prompt_tail),
            ]
        elif session.PRMPT_STYL == 1: # MINIMAL SKULL
            self.message = [
                ('class:parens_open_outer','('),
                ('class:parens_open','('),
                ('class:dps','dps'),
                ('class:parens_close',')'),
                ('class:parens_close_outer',')'),
                ('class:skull','☠️  '),
            ]
        elif session.PRMPT_STYL == 2 or session.PRMPT_STYL == 3 or session.PRMPT_STYL == 4: # MINIMAL
            self.message = [
                ('class:parens_open_outer','('),
                ('class:parens_open','('),
                ('class:dps',session.UID),
                ('class:at','@'),
                ('class:dps',session.HOSTNAME),
                ('class:colon',':'),
                ('class:path',self.path),
                ('class:parens_close',')'),
                ('class:parens_close_outer',')'),
                ('class:prompt',session.prompt_tail),
            ]
        elif session.PRMPT_STYL == 5: # MINIMAL
            if session.UID == "root":
                uid = "#"
            else:
                uid = session.UID
            # break up the path:
            path_array = self.path.split("/")

            self.message = [
                ('class:text_uid'," "+uid+" "),
                ('class:text_host_sep',"▛ "),
                ('class:text_host',session.HOSTNAME+" "),
                ('class:text_path_sep',"▛"),
                ('class:text_path_colon'," ["),
            ]
            self.message.append(('class:text_path_slash',"/"))
            for path in path_array:
                if path != "":
                    self.message.append(("class:text_path",path)) # add the name
                    self.message.append(("class:text_path_slash","/")) # add the slash
            self.message.append(('class:text_path_colon',"]"))
            #self.message.append(('class:prompt_tail_sep',"▛"))
            self.message.append(('class:prompt_tail'," ▸ "))
            #print(self.message)
            #sys.exit(1)

    def __init__(self):
        self.path = os.getcwd()
        ###===========================================
        ## BUILD THEMES HERE, TEST COLORS THOROUGHLY (256bit):
        ###===========================================
        #####
        ### THIS THEME WILL BE DEFAULT WITH DPS.INI:
        if session.PRMPT_STYL == 0:
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
        #####
        ### MINIMAL SKULL THEME
        elif session.PRMPT_STYL == 1:
                self.style = Style.from_dict({
                    # User input (default text).
                    '':          'italic #af5f00',
                    # Prompt.
                    'parens_open': '#af0000',
                    'parens_open_outer': '#af5f00',
                    'dps':       'italic #870000',
                    'parens_close_outer':    '#af5f00',
                    'parens_close':    '#af0000',
                    'skull':    '#8e8e8e',
                })
        elif session.PRMPT_STYL == 2:
            #####
            ### BONEYARD:
            self.style = Style.from_dict({
                # User input (default text).
                '':          'italic #ffffd7',
                'parens_open': 'bold #aaa',
                'parens_open_outer': 'bold #ffffd7',
                'at':       'italic #555',
                'dps':       'underline italic #888',
                'parens_close_outer':    'bold #ffffd7',
                'parens_close':    'bold #aaa',
                'pound':    'bold #aaa',
		        'path': 'italic #ffffd7'
            })
        elif session.PRMPT_STYL == 3:
            #####
            ### 1980s THEME:
            self.style = Style.from_dict({
                # User input (default text).
                '':          'italic #ff0066',
                # Prompt.
                'parens_open': '#d7ff00',
                'parens_open_outer': '#d700af',
                'dps':       'italic bold #d7ff00',
                'colon': 'italic bold #d700af',
                'path': 'italic bold #afff00',
                'parens_close_outer':    '#d700af',
                'parens_close':    '#d7ff00',
                'pound':    '#00aa00',
            })
        elif session.PRMPT_STYL == 5:
            #####
            ### Nouveau: THEME:
            self.style = Style.from_dict({
                # User input (default text).
                'text_host':     'fg:#FFFBDA bg:#822d2d italic bold',
                'text_host_sep':     'fg:#a59784 bg:#822d2d italic bold',
                'text_uid':     'fg:#1e1e1e bg:#a59784 italic bold',
                'text_path':     'fg:#FFFBDA bg: italic bold underline',
                'text_path_sep':     'fg:#822d2d bg:',
                'text_path_slash':     'fg:#a59784 bg: italic',
                'text_path_colon':     'fg:#666 bg: bold',
                'sep':     'fg:#FFFBDA bg:#B44949 ',
                'tip':   'fg:black bg:#FFFBDA italic',
                'prompt_tail':   'bg: fg:#822d2d ',
                'prompt_tail_sep':  'fg:#2e2e2e bg:'
            })

        else:
            #####
            ### DEFAULT THEME:
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
            complete_while_typing=False,
            color_depth=ColorDepth.TRUE_COLOR
        )
    def update_prompt(self):
        self.set_message()
        self.prompt_session.message = self.message

def shell(dps):
    with open(session.LOG_FILENAME) as file:
        for entry in file:
            cmd = entry.split(",")[5]
            if cmd != "":
                dps.prompt_session.history.append_string(cmd.rstrip())
    try:
        last_string = dps.prompt_session.prompt()
        hook_cmd(last_string)
        dps.update_prompt()
    except KeyboardInterrupt:
        #exit_gracefully()
        pass
    except EOFError:
        exit_gracefully()

# standard boilerplate
if __name__ == "__main__":
    print(prompt_ui.bcolors['BOLD']+"\n *** Welcome to the Demon Pentest Shell ("+session.VERSION+")\n *** Type \"exit\" to return to standard shell.\n"+prompt_ui.bcolors['ENDC'])
    dps = DPS() # Prompt-toolkit class instance
    while True:
        shell(dps) #start the app
