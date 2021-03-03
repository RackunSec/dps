### SESSION AND USER INFO:
import ifaddr # NIC info
import socket # for HOSTNAME
import getpass # for logging the username
import datetime # for logging the datetime
import os # for the commands, of course. These will be passed ot the shell.

class Session:
    def __init__(self,version,dps_install_dir):
        self.ADAPTERS = ifaddr.get_adapters() # get network device info
        self.NET_DEV = "" # store the network device
        self.HOSTNAME = socket.gethostname() # hostname for logging
        self.UID = getpass.getuser() # Get the username
        self.REDIRECTION_PIPE = '_' # TODO not needed?
        self.VERSION = version
        self.LOG_DAY = datetime.datetime.today().strftime('%Y-%m-%d') # get he date for logging purposes
        self.LOG_FILENAME = os.path.expanduser("~")+"/.dps/logs/"+self.LOG_DAY+"_dps_log.csv" # the log file is based on the date
        self.OWD=os.getcwd() # historical purposes
        self.VARIABLES = {} # all user-defined variables.
        self.prompt_tail = "# " if self.UID == "root" else "> " # diff root prompt
        self.NEWLOG=False
        self.dps_install_dir = dps_install_dir
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
            self.NEWLOG=True
