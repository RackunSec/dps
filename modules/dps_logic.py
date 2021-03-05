##############################################
## Custom DPS Module.
## Name: Foreach Programming Logic.
## Description: Will iterate ranges and file contents to perform actions on the values.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:
import re
import dps_cmd as run_cmd
import os

## Method: Foreach() programming logic:
def foreach(cmd_delta,session,prompt_ui,dpsrc): # FOREACH
    prompt_ui.bcolors['FAIL']
    prompt_ui.bcolors['ENDC']
    cmd_args = re.sub("^foreach(\s+)?","",cmd_delta)
    if cmd_args == "":
        session.help.msg("foreach",session,prompt_ui)
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
                    if re.search(">(\s+)?[^>]+",cmd_delta): # FILE OUTPUT!
                        file_output = True
                        file_name = re.sub("[^>]+>\s+(.)","\\1",cmd_delta)
                        if not re.search("/",file_name): # current directory?
                            file_name = os.getcwd()+"/"+file_name
                        try: # overwrite the file
                            os.remove(file_name)
                        except: # file did not exist. OK.
                            pass
                    else:
                        file_output = False
                    ## NOW, we loop!:
                    for i in int_range: # 0..9
                        do_re = re.compile("\$"+var)
                        do_cmd = re.sub(do_re,str(i),do)
                        if file_output == True: # output to a file with >>

                            cmd_split = re.split(">+",do_cmd)
                            if(len(cmd_split)==2):
                                do_cmd = cmd_split[0]+" | tee -a "+cmd_split[1]
                            else:
                                print(f"{FAIL}Error in syntax or file name.{ENDC}")
                                return
                        run_cmd.run(do_cmd,dpsrc,session,prompt_ui)
                elif os.path.exists(object): # this is a file
                    # should we output to a file?
                    if re.search(">(\s+)?[^>]+",cmd_delta): # FILE OUTPUT!
                        file_output = True
                        file_name = re.sub("[^>]+>\s+(.)","\\1",cmd_delta)
                        if not re.search("/",file_name): # current directory?
                            file_name = os.getcwd()+"/"+file_name
                        try: # overwrite the file
                            os.remove(file_name)
                        except: # file did not exist. OK.
                            pass
                    else:
                        file_output = False
                    if not re.search("/",file_name): # current directory?
                        file_name = os.getcwd()+"/"+file_name
                    # pull out what to do with the entry:
                    do = re.sub("^[^:]+:","",cmd_delta)
                    with open(object) as object_file:
                        for entry in object_file:
                            # replace entry with $var in do:
                            do_re = re.compile("\$"+var)
                            do_cmd = re.sub(do_re,entry.strip(),do)
                            if file_output == True:
                                run_cmd.run(do_cmd+"| tee -a "+file_name,dpsrc,session,prompt_ui)
                            else:
                                run_cmd.run(do_cmd,dpsrc,session,prompt_ui)

                else:
                    error("Could not access object: "+object,"")
        else:
            error("Programming logic syntax error. Please check the documentation.","")
