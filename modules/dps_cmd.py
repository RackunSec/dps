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
import sys # for exit
import subprocess
## DPS REQUIREMENTS:
import dps_log
import dps_env
import dps_stats
import dps_uid_gen
import dps_www
import dps_wifi
import dps_update
import dps_self_destruct
import dps_logic as logic

## Exit gracefully to default shell:
def exit_gracefully(): # handle CTRL+C or CTRL+D, or quit, or exit gracefully:
    sys.exit(0);

## Method: Run Commands.
def run(cmd,dpsrc,session,prompt_ui):
    WARN=prompt_ui.bcolors['WARN']
    FAIL=prompt_ui.bcolors['FAIL']
    BOLD=prompt_ui.bcolors['BOLD']
    OKGREEN=prompt_ui.bcolors['OKGREEN']
    ENDC=prompt_ui.bcolors['ENDC']
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
        all_paths = dpsrc.paths # this could change since we also have cwd (.)
        if os.getcwd() not in all_paths:
            all_paths.append(os.getcwd())
        for path in all_paths:
            if bin in os.listdir(path):
                bin_paths.append(path+"/"+bin)
        if bin in session.BASHBI: # pass to Bash:
            subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
            return
        if len(bin_paths)>1:
            print(f"{WARN}WARNING: binary file ({bin}) discovered in multiple paths:\n--------------------------------{ENDC}")
            count = 0;
            for path in bin_paths:
                print(f"{BOLD}[{OKGREEN}{count}{prompt_ui.bcolors['ENDC']}{BOLD}]{ENDC} {OKGREEN}{path}{ENDC}")
                count+=1
            print(f"\n{BOLD}[?]{ENDC} Please choose one:",end=" ")
            ans=int(input())
            try:
                if bin_paths[ans]:
                    #print(f"You chose: {ans} which is {bin_paths[ans]}")
                    subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
                    return
            except:
                print(f"{FAIL}INDEX: {str(ans)} out of range of list provided to you.{ENDC}")
                return
        elif len(bin_paths)==1: # we found the command (binary):
            subprocess.call(["/bin/bash", "--init-file","/root/.bashrc", "-c", cmd])
            return
        else:
            print(f"{prompt_ui.bcolors['FAIL']}Binary \"{bin}\" not found in paths.\n  Check your [Paths] within the DPS configuration file.")
            return
    return

## Method: hook the command entered for built-in's etc:
def hook(cmd,dpsrc,session,prompt_ui):
    ###
    ## First, set aliases:
    ###
    cmd_delta = cmd
    cmd_count = cmd.split("|") # how many commands were there?
    if len(cmd_count)>1:
        new_cmd = []
        for cmd_count_iter in cmd_count:
            #print(f"cmd_count_iter:{cmd_count_iter}") # DEBUG
            if len(dpsrc.aliases) > 0 and cmd_count_iter.split()[0] in dpsrc.aliases: # we will rewrite the command with the alias.
                cmd_split = cmd_count_iter.split() # split the command up to get the first element
                cmd_base = re.sub(cmd_split[0],dpsrc.aliases[cmd_split[0]],cmd_split[0]) # set alias
                cmd_split[0]=cmd_base # overwrite it
                new_cmd.append(" ".join(cmd_split))
            else:
                new_cmd.append(cmd_count_iter) # place it in, untouched.
        cmd_delta=" | ".join(new_cmd)
    else:
        cmd_strip = cmd.rstrip()
        if len(dpsrc.aliases) > 0 and cmd_strip in dpsrc.aliases:
            cmd_delta = re.sub(cmd_strip,dpsrc.aliases[cmd_strip],cmd_strip) # set alias
    cmd_delta = re.sub("~",os.path.expanduser("~"),cmd_delta)
    cmd_delta = re.sub("^\s+","",cmd_delta) # remove any prepended spaces
    ###
    ## Next, interpolate any variables:
    ###
    if re.match(".*\{[^\}]+\}.*",cmd_delta) and not re.match("awk\s",cmd_delta): # AWK actually uses this syntax too.
        # I chose a very unique variablename here on purposes to not collide.
        var123_0x031337 = re.sub(r"^[^\{]+{([^\}]+)}.*$","\\1",cmd_delta) # TODO interpolate multiple times! (use a while loop) (wait, can you do global replace?)
        var_re = re.compile("{"+var123_0x031337+"}")
        if session.VARIABLES.get(var123_0x031337): # it exists
            cmd_delta = re.sub(var_re,session.VARIABLES[var123_0x031337],cmd_delta)
        else:
            error.msg(f"Variable declared not yet defined: {var123_0x031337}","def",session,prompt_ui)
            return
    ###
    ## Now, we log the command:
    ###
    if cmd_delta!="": # do not log enter presses, derp.
        dps_log.cmd(cmd_delta,session,prompt_ui) # first, log the command.
    # Handle built-in commands:
    if cmd_delta == "exit" or cmd_delta == "quit":
        exit_gracefully()

    ### ===============================================
    ### DEFINE HOW TO HANDLE YOUR NEW MODULES! (9387ee)
    ### ===============================================

    ### Programming logic:
    elif cmd_delta.startswith("foreach"): # foreach (file.txt) as line: echo line
        logic.foreach(cmd_delta,session,prompt_ui,dpsrc) #
    elif cmd_delta.startswith("dps_env"): # foreach (file.txt) as line: echo line
        dps_env.env(session,prompt_ui,dpsrc) #
    elif cmd_delta.startswith("dps_www_commentscrape"):
        dps_www.comment_scrape(cmd_delta,session,prompt_ui)
    elif cmd_delta.startswith("dps_www_verbs"):
        dps_www.verb_test(cmd_delta,session,prompt_ui)
    elif cmd_delta.startswith("dps_self_destruct"):
        dps_self_destruct.self_destruct(session,prompt_ui)
        return
    elif cmd_delta.startswith("dps_wifi"):
        dps_wifi.set(cmd_delta,session,prompt_ui)
    elif cmd_delta.startswith("def "): # def var: val
        dps_env.define_var(cmd,session,prompt_ui)
    elif re.match("^\s?sudo",cmd_delta): # for sudo, we will need the command's full path:
        sudo_regexp = re.compile("sudo ([^ ]+)")
        cmd_delta=re.sub(sudo_regexp,'sudo $(which \\1)',cmd_delta)
        run(cmd_delta,dpsrc,session,prompt_ui)
        return
    elif cmd_delta.startswith("dps_uid_gen"):
        dps_uid_gen.gen_uids(cmd_delta,session,prompt_ui)

    elif(cmd_delta=="dps_stats"):
        dps_stats.show(prompt_ui)
    elif(cmd_delta=="dps_update"):
        dps_update.app(session,prompt_ui)
    elif(cmd_delta=="dps_alias"):
        dps_env.show_alias(dpsrc,prompt_ui)
    elif(cmd_delta.startswith("dps_config")):
        args = re.sub("dps_config","",cmd_delta).split() # make an array
        if len(args) > 0:
            dps_env.prompt(args,dpsrc,prompt_ui)
        else:
            error.msg("Not enough arguments.","dps_config",session,prompt_ui)
    elif(cmd_delta.startswith("help")):
        args = cmd_delta.split()
        if(len(args)>1):
            session.help.msg(args[1],session,prompt_ui)
        else:
            session.help.msg("",session,prompt_ui)

    ###---------
    ## VERSION @override:
    ###---------
    elif(cmd_delta=="version"):
        print(f"{prompt_ui.bcolors['OKGREEN']}Demon Pentest Shell - {session.VERSION} {prompt_ui.bcolors['ENDC']}")
    ###---------
    ### WARN Leaving DPS:
    ###---------
    elif(cmd_delta=="bash"):
        print(f"{prompt_ui.bcolors['WARN']}WARNING - Leaving DPS for Bash shell (CTRL+D to return to DPS){prompt_ui.bcolors['ENDC']}")
        run(cmd_delta,dpsrc,session,prompt_ui)

    ###---------
    ## LS @override:
    ###---------
    elif(re.match("^ls",cmd_delta)):
        cmd_delta = re.sub("^ls","ls --color=auto",cmd)
        run(cmd_delta,dpsrc,session,prompt_ui)
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
            error.msg("Path does not exist: "+where_to,"",session,prompt_ui)
    else: # Any OTHER command:
        run(cmd_delta,dpsrc,session,prompt_ui)
    return
