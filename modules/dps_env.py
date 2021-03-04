##############################################
## Custom DPS Module.
## Name: Aliasing commands.
## Description: Set an alias for a command as defined in ~/.dps/.dpsrc file.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
## TODO: Set/Update aliases.
##

## REQUIREMENTS:
import re
import os

## Method: show your aliases set in .dpsrc:
def show_alias(dpsrc,prompt_ui):
    ENDC=prompt_ui.bcolors['ENDC']
    BOLD=prompt_ui.bcolors['BOLD']
    OKGREEN=prompt_ui.bcolors['OKGREEN']
    print(f"{BOLD}\n ▿ DPS.ini Defined [ALIASES] ▿ {ENDC}")
    for alias in dpsrc.aliases:
        print(f"  ◦ Alias found for {OKGREEN}{alias}{ENDC} as '{OKGREEN}{dpsrc.aliases[alias]}{ENDC}'")
    print("")
    return

## Method show environment
def env(session,prompt_ui,dpsrc):
    # Show all sesstings in session object:
    print(f"\n[Networking]")
    print(f"{session.ADAPTERS}")
    print(f"\n[Aliases]")
    for alias in dpsrc.aliases:
        print(f"{alias}: {dpsrc.aliases[alias]}")
    print(f"\n[Variables]")
    for var in session.VARIABLES:
        print(f"{var}: {session.VARIABLES[var]}")
    print(f"\n[Logs]")
    print(f"Current: {session.LOG_FILENAME}")
    print(f"\n[File System]")
    print(f"Old working directory: {session.OWD}")
    print(f"Current working directory: {os.getcwd()}")
    return

## Method: define a session variable:
def define_var(cmd,session,prompt_ui):
    if len(cmd.split())==3:
        WARN=prompt_ui.bcolors['WARN']
        ENDC=prompt_ui.bcolors['ENDC']
        BOLD=prompt_ui.bcolors['BOLD']
        OKGREEN=prompt_ui.bcolors['OKGREEN']
        FAIL=prompt_ui.bcolors['FAIL']
        if re.match("^[^:]+:\s+[^\s]+$",cmd): # syntax [ OK ]
            key=cmd.split()[1]
            key=re.sub(":$","",key) # drop the colon
            val=cmd.split()[2]
            print(f"\n ▹ Defining variable {BOLD}{OKGREEN}{key}{ENDC} value {BOLD}{OKGREEN}{val}{ENDC} for this DPS session.\n")
            session.VARIABLES[key]=val
            return
        else:
            print(f"\n{FAIL} ✖ Syntax for \"def\" incorrect. See Below.{ENDC}")
            session.help.msg("def",session,prompt_ui)
    else:
        session.help.msg("def",session,prompt_ui)


## Method prompt() -- update the configuration file's prompt setting.
def prompt(args,dpsrc,prompt_ui):
    WARN=prompt_ui.bcolors['WARN']
    ENDC=prompt_ui.bcolors['ENDC']
    BOLD=prompt_ui.bcolors['BOLD']
    OKGREEN=prompt_ui.bcolors['OKGREEN']
    FAIL=prompt_ui.bcolors['FAIL']
    if len(args) > 1:
        if args[0] == "prompt": # set it in the config file:
            #try:
            print(f"{OKGREEN} ▹ {ENDC} Adding {str(args[1])} as prompt_theme in {dpsrc.dps_config_file}")
            dpsrc.configparser.read(dpsrc.dps_config_file)
            dpsrc.configparser.sections()
            dpsrc.configparser.set('Style','prompt_theme',args[1]) # TODO int() ?
            with open(dpsrc.dps_config_file, 'w') as config_file:
                dpsrc.configparser.write(config_file)
            print(f"{OKGREEN}Prompt setting updated. Restart DPS to take effect.")
