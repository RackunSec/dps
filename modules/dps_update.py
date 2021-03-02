##############################################
## Custom DPS Module.
## Name: Updater Tool.
## Description: Does Git PULL
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import git

## Method: app() -- update the application
def app(session,prompt_ui):
    # pull an updated version from GitHUB and rewrite the specified path in [Paths]['DPS_bin_path'] from the ini file:
    FAIL=prompt_ui.bcolors['FAIL']
    ENDC=prompt_ui.bcolors['ENDC']
    OKGREEN=prompt_ui.bcolors['OKGREEN']
    BOLD=prompt_ui.bcolors['BOLD']
    try:
        g = git.cmd.Git(session.DPSBINPATH)
        g.stash('save')
        g.pull(force=True)
        print(f"\n{BOLD} ▹ {ENDC} {OKGREEN}Successfully pulled changes to local repository: {session.DPSBINPATH} {ENDC}\n")
    except:
        print(f"{FAIL} ✖ Something went wrong when trying to perform git operations. {ENDC}")

## Method config() -- update the configuration file
def config(args,session,prompt_ui):
    if len(args) > 1:
        if args[0] == "prompt": # set it in the config file:
            #try:
            print(f"{OKGREEN} ▹ {ENDC} Adding "+str(args[1])+" as prompt_theme in "+session.CONFIG_FILENAME)
            session.CONFIG.read(session.CONFIG_FILENAME)
            session.CONFIG.sections()
            session.CONFIG.set('Style','prompt_theme',args[1]) # TODO int() ?
            with open(session.CONFIG_FILENAME, 'w') as config_file:
                session.CONFIG.write(config_file)
