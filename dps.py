#!/usr/bin/env python3
# The Demon (DEMON LINUX) Penetration Testing Shell
# Custom shell for superior logging during a penetration test.
# logs as CSV with time,hostname,network:ip,who,command in the ~/.dps/ directory
# requires Python 3+
#
# 2021 - Douglas Berdeaux, Matthew Creel
#
#
### IMPORT LIBRARIES:
version = "v1.3.17(póg mo thóin)" # update this each time we push to the repo (version (year),(mo),(day),(revision))
import os # for the commands, of course. These will be passed ot the shell.
from sys import exit as exit # for exit.
from sys import path as path # for reading files.
from re import sub as sub # regexp substitutions
from re import split as resplit # regexp splitting
from re import match as match # regexp match
from prompt_toolkit import prompt, ANSI # for input
from prompt_toolkit.completion import WordCompleter # completer function (feed a list)
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.styles import Style # Style the prompt
from prompt_toolkit.output.color_depth import ColorDepth # colors for prompt
## My own classes:
dps_install_dir=os.path.dirname(os.path.realpath(__file__)) # where am I installed on your FS?
path.append(dps_install_dir+"/modules/")
path.append(dps_install_dir+"/classes/")
import dps_cmd as dps_cmd
import dps_help as help
# class files:
import dps_session
import dpsrc as dpsrc
import dps_prompt_ui as prompt_ui
from datetime import datetime

prompt_ui = prompt_ui.prompt_ui() # Instantiet the above.
dpsrc=dpsrc.DPSrc(dps_install_dir) # create  global resource object

# instantiate them:
session = dps_session.Session(version,dps_install_dir) # Object with Session data and user config
session.init_config() # initialize the configuration.
session.help = help

# Get the adapter and IP address:
def get_net_info():
    for adapter in session.ADAPTERS: # loop through adapters
        if match("^e..[0-9]+",adapter.nice_name):
            try:
                session.NET_DEV = adapter.nice_name+":"+adapter.ips[0].ip
            except:
                print(f"{prompt_ui.bcolors['FAIL']}No network address is ready. Please get a network address before continuing for logging purposes.","",session,prompt_ui)
                session.help.msg("dps_config",session,prompt_ui) # show help for config.
                session.NET_DEV = "0.0.0.0" # no address?
get_net_info()

###===========================================
## GENERAL METHODS FOR HANDLING THINGS:
###===========================================
def exit_gracefully(): # handle CTRL+C or CTRL+D, or quit, or exit gracefully:
    exit(0);

###=======================================
## OUR CUSTOM COMPLETER: (a nightmare)
###=======================================
class DPSCompleter(Completer):
    def __init__(self, cli_menu):
        self.path_completer = PathCompleter()
    def get_completions(self, document, complete_event):

        word_before_cursor = document.get_word_before_cursor()
        try:
            cmd_line = document.current_line.split() # get the real deal here.
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
                    path=sub("foreach.","",current_str)
                    if path.startswith("/"):
                        path_to=sub("[^/]+$","",path) # chop off end text
                        match = sub(".*/","",path) # greedily remove path
                        try:
                            options = os.listdir(path_to)
                        except:
                            options = []
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
                        if cmd_line[0] == "help": # capture help
                            tab_com = current_str.split("/")[-1]
                            options = []
                            for builtin in help.modules_list:
                                options.append(builtin)
                            for opt in options:
                                if opt.startswith(tab_com):
                                    yield Completion(opt, -len(current_str),style='italic')
                            return
                        if "/" in cmd_line[-1]: # directory traversal?
                            if match("^[A-Za-z0-9\.]",cmd_line[-1]) and cmd_line[-1].endswith("/"): # e.g.: cd Documents/{TAB TAB}
                                dir = os.getcwd()+"/"+cmd_line[-1]
                                try:
                                    options = os.listdir(dir)
                                except:
                                    options = []
                                for opt in options:
                                    opt2 = dir+opt
                                    if os.path.isdir(opt2):
                                        opt2 += "/" # this is a directory
                                    yield Completion(opt2, -len(current_str),style='italic')
                                return
                            elif match("^[A-Za-z0-9\.]",cmd_line[-1]) and (not cmd_line[-1].endswith("/")): # e.g.: cd Documents/Te{TAB TAB}
                                tab_com = current_str.split("/")[-1]
                                dir = os.getcwd()+"/"+sub("[^/]+$","",current_str)
                                try:
                                    options = os.listdir(dir)
                                except:
                                    options = []
                                for opt in options:
                                    if opt.startswith(tab_com):
                                        yield Completion(dir+opt, -len(current_str),style='italic')
                                return
                            elif match("^/",cmd_line[-1]):
                                # get path:
                                path_to = sub("[^/]+$","",cmd_line[-1])
                                what_try = cmd_line[-1].split("/")[-1]
                                try:
                                    options = os.listdir(path_to)
                                except:
                                    options = []
                                for opt in options:
                                    if opt.startswith(what_try):
                                        if(os.path.isdir(path_to+opt+"/")): # is a directory - append a slash to "keep going" with TAB:
                                            yield Completion(path_to+opt+"/", -len(current_str),style='italic')
                                        else: # not a directory:
                                            yield Completion(path_to+opt, -len(current_str),style='italic')
                                return

                        # Get the path off of the document.current_line object:
                        current_str = cmd_line[len(cmd_line)-1]
                        path_to = sub("(.*)/[^/]+$","\\1/",cmd_line[1])
                        object = cmd_line[-1].split("/")[-1] # last element, of course.

                        if path_to.startswith("~/"):
                            dir = os.path.expanduser(path_to)
                        elif path_to.startswith("/"): # full path:
                            dir = path_to
                        else:
                            dir = os.getcwd()

                        # now that we have defined "dir" let's get the contents:
                        try:
                            options = list(set(os.listdir(dir))) # this will only show unique values.
                        except:
                            options = []
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
                        #print("dot slash!") # DEBUG
                        cmd = sub(".+/","",cmd_line[0]) # remove [./this/that/]foo
                        curr_dir_in_path = sub("[^/]+$","",cmd_line[0])
                        try:
                            options = os.listdir(curr_dir_in_path)
                        except:
                            options = []
                        final_options = [] # what we yield.
                        for opt in options:
                            if opt.startswith(cmd):
                                final_options.append(opt) # just get rid of it.
                        for opt in final_options:
                            if os.path.isdir(curr_dir_in_path+opt):
                                yield Completion(curr_dir_in_path+opt+"/", -len(current_str),style='italic')
                            else:
                                yield Completion(curr_dir_in_path+opt, -len(current_str),style='italic')
                        return # goodbye!
                    elif cmd_line[0].startswith("/"): # defining full path, eh?
                        cmd = sub(".*/","",cmd_line[0]) # remove [./this/that/]foo
                        curr_dir_in_path = sub("[^/]+$","",cmd_line[0])
                        try:
                            options = os.listdir(curr_dir_in_path)
                        except:
                            options = []
                        final_options = [] # what we yield.
                        for opt in options:
                            if opt.startswith(cmd):
                                final_options.append(opt) # just get rid of it.
                        for opt in final_options:
                            try:
                                if os.path.isdir(curr_dir_in_path+opt):
                                    yield Completion(curr_dir_in_path+opt+"/", -len(current_str),style='italic')
                                else:
                                    yield Completion(curr_dir_in_path+opt, -len(current_str),style='italic')
                            except:
                                yield Completion(curr_dir_in_path+opt, -len(current_str),style='italic')
                        return # goodbye!
                    # Run from PATH:
                    else: # just pull in what we need - not everything:
                        options = []
                        for builtin in help.modules_list:
                            options.append(builtin)
                        options += session.BASHBI # append Bash built-ins as they don't live in $PATH
                        for path in dpsrc.paths:
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


        if dpsrc.prompt_theme == 0: # DEFAULT SHELL
            self.message = [
                ('class:username', session.UID),
                ('class:at','@'),
                ('class:host',session.HOSTNAME),
                ('class:colon',':'),
                ('class:path',self.path),
                ('class:dps','(dps)'),
                ('class:pound',session.prompt_tail),
            ]
        elif dpsrc.prompt_theme == 1: # MINIMAL SKULL
            self.message = [
                ('class:parens_open_outer','('),
                ('class:parens_open','('),
                ('class:dps','dps'),
                ('class:parens_close',')'),
                ('class:parens_close_outer',')'),
                ('class:skull','☠️  '),
            ]
        elif dpsrc.prompt_theme == 2 or dpsrc.prompt_theme == 3 or dpsrc.prompt_theme == 4: # MINIMAL
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
        elif dpsrc.prompt_theme == 5: # Nouveau
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
            self.message.append(('class:prompt_tail'," ▸ "))

        elif dpsrc.prompt_theme == 6: # Daemo
            if session.UID == "root":
                uid = "#"
            else:
                uid = session.UID
            # break up the path:
            path_array = self.path.split("/")

            self.message = [
                ('class:text_uid'," "+uid+" "),
                ('class:sep',"▸ "),
                ('class:text_host',session.HOSTNAME+" "),
                ('class:sep',"▸"),
                ('class:text_path_brackets'," ["),
            ]
            self.message.append(('class:text_path_slash',"/"))
            for path in path_array:
                if path != "":
                    self.message.append(("class:text_path",path)) # add the name
                    self.message.append(("class:text_path_slash","/")) # add the slash
            self.message.append(('class:text_path_brackets',"]"))
            self.message.append(('class:prompt'," ▸ "))

        elif dpsrc.prompt_theme == 7: # Dropped
            # break up the path:
            path_array = self.path.split("/")

            self.message = [
                ('class:text_uid'," "+session.UID+" "),
                ('class:text_host'," "+session.HOSTNAME+" "),
                ('class:text_path_brackets',"["),
            ]
            self.message.append(('class:text_path_slash',"/"))
            for path in path_array:
                if path != "":
                    self.message.append(("class:text_path",path)) # add the name
                    self.message.append(("class:text_path_slash","/")) # add the slash
            self.message.append(('class:text_path_brackets',"]"))
            self.message.append(('class:prompt',"\n┗▸ "))

        elif dpsrc.prompt_theme == 8: # Brew
            # break up the path:
            self.message = [
                ('class:khaki',"   "),
                ('class:light',"Pentest"),
            ]
            if "TARGET" in session.VARIABLES:
                target = f"{session.VARIABLES['TARGET']}"
                self.message.append(('class:khaki',"(")),
                self.message.append(('class:target',target)),
                self.message.append(('class:khaki',")")),

            self.message.append(('class:dark'," "))
            self.message.append(('class:khaki',""))
            self.message.append(('class:light'," "))

        elif dpsrc.prompt_theme == 9: # Athens
            # break up the path:
            path_array = self.path.split("/")

            self.message = [
                ('class:whitebg', f" {session.UID} "),
                ('class:text_host_sep',"▛ "),
                ('class:bluebg', f"{session.HOSTNAME} "),
                ('class:text_path_sep',"▛"),
                ('class:yellow', " ⚡"),
                ('class:blue', "[")
            ]
            self.message.append(('class:blue',"/"))
            for path in path_array:
                if path != "":
                    self.message.append(("class:white",path)) # add the name
                    self.message.append(("class:blue","/")) # add the slash
            self.message.append(('class:blue', "]\n"))
            self.message.append(('class:white', "λ "))

        elif dpsrc.prompt_theme == 10: # Japan
            # break up the path:
            current_dir = self.path.rsplit("/", 2)[1]

            self.message = [
                ('class:whitebg', f" {session.UID} "),
                ('class:char', " ※ "),
                ('class:redfg', "("),
                ('class:whitefg', f"{current_dir}"),
                ('class:redfg', ")"),
                ('class:char', "⥤  ")
            ]


        elif dpsrc.prompt_theme == 11: # Polar Mint
            # break up the path:
            self.message = [
                ('class:dark',"   "),
                ('class:light',"Pentest"),
            ]
            if "TARGET" in session.VARIABLES:
                target = f"{session.VARIABLES['TARGET']}"
                self.message.append(('class:khaki',"(")),
                self.message.append(('class:dark',target)),
                self.message.append(('class:khaki',")")),

            self.message.append(('class:dark'," "))
            self.message.append(('class:khaki',""))
            self.message.append(('class:light'," "))

    def __init__(self):
        self.path = os.getcwd()
        ###===========================================
        ## BUILD THEMES HERE, TEST COLORS THOROUGHLY (256bit):
        ###===========================================
        #####
        ### MINIMAL SKULL THEME
        if dpsrc.prompt_theme == 1:
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
        elif dpsrc.prompt_theme == 2:
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
        elif dpsrc.prompt_theme == 3:
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
        elif dpsrc.prompt_theme == 5:
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

        elif dpsrc.prompt_theme == 6:
            #####
            ### DAEMO: THEME:
            self.style = Style.from_dict({
                # User input (default text).
                '':'', #italic #329da8',
                # Prompt.
                'text_uid': 'fg:#fff9e6 bg:#222',
                'sep': 'fg:#aaa bg:#222',
                'prompt': 'fg:#aaa bg:',
                'text_host': 'italic bold fg:#fff9e6 bg:#222',
                'text_path': 'italic fg:#7d7d7d bg:#222',
                'text_path_brackets': 'bold fg:#7d7d7d bg:#222',
                'text_path_slash': 'italic bold fg:#555 bg:#222',
            })

        elif dpsrc.prompt_theme == 7:
            #####
            ### DROPPED: THEME:
            self.style = Style.from_dict({
                # User input (default text).
                '':'#fff bold italic', #italic #329da8',
                # Prompt.
                'text_uid': 'fg:#fff9e6 bg:#333',
                'sep': 'fg:#aaa bg:',
                'prompt': 'fg:#333 bg:',
                'text_host': 'italic bold fg:#fff9e6 bg:',
                'text_path': 'italic fg:#7d7d7d bg:',
                'text_path_brackets': 'bold fg:#7d7d7d bg:',
                'text_path_slash': 'italic bold fg:#555 bg:',
            })

        elif dpsrc.prompt_theme == 8:
            #####
            ### BREW: THEME:
            self.style = Style.from_dict({
                # User input (default text).
                '':'fg:#aaa italic bold',
                'mug':'noitalic nobold fg:#4f3218',
                'dark':'noitalic nobold fg:#423826',
                'khaki':'noitalic nobold fg:#6b5c43',
                'light':'noitalic nobold fg:#96815d',
                'target':'nobold fg:#96815d'
            })

        elif dpsrc.prompt_theme == 9:
            #####
            ### ATHENS: THEME:
            self.style = Style.from_dict({
                '':'fg:#ffffff italic ',
                'white':'noitalic nobold fg:#ffffff',
                'blue':'noitalic nobold fg:#00b3eb',
                'yellow':'noitalic fg:#ffff00',
                'whitebg':'noitalic  fg:#00b3eb  bg:#ffffff',
                'bluebg':'noitalic  bg:#00b3eb fg:#ffffff',
                'text_host_sep':'italic bold fg:#ffffff bg:#00b3eb',
                'text_path_sep':'italic bold fg:#00b3eb'
            })

        elif dpsrc.prompt_theme == 10:
            #####
            ### JAPAN: THEME:
            self.style = Style.from_dict({
                '':'fg:#F80623',
                'whitebg':'bg:#ffffff',
                'whitefg':'italic fg:#ffffff',
                'redfg':'italic fg:#F80623',
                'char':'fg:#ffffff'
            })

        elif dpsrc.prompt_theme == 11:
            #####
            ### POLAR MINT: THEME:
            self.style = Style.from_dict({
                # User input (default text).
                '':'fg:#b1fad8 italic bold',
                'leaf':'noitalic nobold fg:#b1fad8',
                'dark':'noitalic nobold fg:#00ff88',
                'khaki':'noitalic nobold fg:#66ffb8',
                'light':'noitalic nobold fg:#b1fad8',
                'target':'nobold fg:#96815d'
            })

        else:
            #####
            ### PROMPT_THEME IS EITHER 0 OR OUT OF RANGE
            ### THIS THEME WILL BE DEFAULT WITH .DPSRC:
            dpsrc.prompt_theme = 0
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
            cmd = resplit(r'[^\\],',entry)[5]
            if cmd != "":
                dps.prompt_session.history.append_string(cmd.rstrip())
    try:
        last_string = dps.prompt_session.prompt()
        dps_cmd.hook(last_string,dpsrc,session,prompt_ui)
        dps.update_prompt()
    except KeyboardInterrupt:
        #exit_gracefully()
        pass
    except EOFError:
        exit_gracefully()

# standard boilerplate
if __name__ == "__main__":
    print(prompt_ui.bcolors['BOLD']+"\n ▹▹▹ Welcome to the Demon Pentest Shell ("+session.VERSION+")\n ▹▹▹ Type \"exit\" to return to standard shell.\n"+prompt_ui.bcolors['ENDC'])
    if session.NEWLOG==True:
        print(f"{prompt_ui.bcolors['OKGREEN']}New log file created for today's sessions ({session.LOG_FILENAME})\n")
    dps = DPS() # Prompt-toolkit class instance
    while True:
        shell(dps) #start the app
