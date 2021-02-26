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
    "This is a docstring."
    # pull an updated version from GitHUB and rewrite the specified path in [Paths]['DPS_bin_path'] from the ini file:
    try:
        g = git.cmd.Git(session.DPSBINPATH)
        g.stash('save')
        g.pull(force=True)
        print(f"\n{prompt_ui.bcolors['BOLD']}[i]{prompt_ui.bcolors['ENDC']} {prompt_ui.bcolors['OKGREEN']}Successfully pulled changes to local repository: {session.DPSBINPATH} {prompt_ui.bcolors['ENDC']}\n")
    except:
        print(f"{prompt_ui.bcolors['BOLD']}[!]{prompt_ui.bcolors['FAIL']} Something went wrong when trying to perform git operations. {prompt_ui.bcolors['ENDC']}")

## Method config() -- update the configuration file
def config(args,session,prompt_ui):
    if len(args) > 1:
        if args[0] == "prompt": # set it in the config file:
            #try:
            print(f"{prompt_ui.bcolors['OKGREEN']}[i]{prompt_ui.bcolors['ENDC']} Adding "+str(args[1])+" as PRMPT_STYL in "+session.CONFIG_FILENAME)
            session.CONFIG.set('Style','PRMPT_STYL',args[1]) # TODO int() ?
            with open(session.CONFIG_FILENAME, 'w') as config_file:
                session.CONFIG.write(config_file)
