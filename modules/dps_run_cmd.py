##############################################
## Custom DPS Module.
## Name: Command Runner.
## Description: Runs commands given by the user by passing them to Bash through subprocess.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import re
import os
import subprocess

## Method: Run Commands.
def run(cmd,session,prompt_ui):
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
        if bin in session.BASHBI: # pass to Bash:
            subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
            return
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
