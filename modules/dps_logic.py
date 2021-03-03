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
import dps_run_cmd as run_cmd

## Method: Foreach() programming logic:
def foreach(cmd_delta,session,prompt_ui,dpsrc): # FOREACH
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
                    for i in int_range: # 0..9
                        do_re = re.compile("\$"+var)
                        do_cmd = re.sub(do_re,str(i),do)
                        #print(f"[pl] cmd: "+do_cmd+" var: "+var)
                        run_cmd.run(do_cmd,dpsrc,session,prompt_ui)
                elif os.path.exists(object): # this is a file
                    # pull out what to do with the entry:
                    do = re.sub("^[^:]+:","",cmd_delta)
                    with open(object) as object_file:
                        for entry in object_file:
                            # replace entry with $var in do:
                            do_re = re.compile("\$"+var)
                            do_cmd = re.sub(do_re,entry.strip(),do)
                            run_cmd.run(do_cmd,dpsrc,session,prompt_ui)
                else:
                    error("Could not access object: "+object,"")
        else:
            error("Programming logic syntax error. Please check the documentation.","")
