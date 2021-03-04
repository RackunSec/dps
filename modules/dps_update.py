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
        g = git.cmd.Git(session.dps_install_dir)
        g.stash('save')
        g.pull(force=True)
        print(f"\n{OKGREEN}Successfully pulled changes to local repository: {session.dps_install_dir}\n -- Restart shell to take effect. {ENDC}\n")
    except:
        print(f"{FAIL} ✖ Something went wrong when trying to perform git operations. {ENDC}")
