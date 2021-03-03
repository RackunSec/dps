##############################################
## Custom DPS Module.
## Name: Help Dialogs.
## Description: Show help.msg() for each module. This will need updated for every module added.
## Author: RackünSec
## Author URL: https://github.com/RackunSec/
##
##

## REQUIREMENTS:

## Entire Help Object (must be updated when a module is added to DPS):
modules_categories=['System','Pentest','Pentest-WWW','Pentest-Wi-Fi','Logic']
modules_list={
    'dps_stats':
        {'title':'DPS Statistics Information',
            'desc':'Statistics for all log files and session data. This is produced from the local DPS ~/.dps/ directory.',
            'category':'System',
            'args':[],
            'syntax_examples':['dps_stats'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_env':
        {'title':'DPS Session and Environment Information',
            'desc':'Displays all session and environment information.',
            'category':'System',
            'args':['var (optional)'],
            'syntax_examples':['dps_env'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_self_destruct':
        {'title':'DPS Log Shredding',
            'desc':'After penetration test, shred all logs located in the local DPS ~/.dps/logs/ directory. Ensure that a backup was made beforehand!',
            'category':'System',
            'args':[],
            'syntax_examples':['dps_self_destruct'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_alias':
        {'title':'DPS Aliases Configuration',
            'desc':'Aliases for commands and binaries (including arguments).',
            'category':'System',
            'args':[''],
            'syntax_examples':['dps_alias'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_update':
        {'title':'Update the Demon Pentest Shell to Latest Version',
            'desc':'Update the Demon Pentest Shell to Latest Version from RackunSec\'s GitHUB repository. This must be done as root user if updating for all users.',
            'args':[''],
            'category':'System',
            'syntax_examples':['dps_update'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'foreach':
        {'title':'DPS Foreach Loop Iterator',
            'desc':'Loop over a range or file and perform actions on each entry.',
            'args':['(path to file)','as (entry variable)',': (stuff to do per entry)'],
            'category':'Logic',
            'syntax_examples':['foreach(/path/to/file.txt) as line: echo $line','foreach(m..n) as int: nmap 192.168.1.$int'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'def':
        {'title':'DPS Variable Definitions',
            'desc':'Define variables and use them in commands.',
            'args':['(Variable Name)','(Variable Value)'],
            'category':'System',
            'syntax_examples':['def TARGET 192.168.1.1','nmap {TARGET}'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_uid_gen':
        {'title':'User ID Generation Tool',
            'desc':'Provide a CSV File with: First, Last fields to generate user IDs, Emails, etc. used for penetration testing.',
            'args':['(format specifier)','(csv file)'],
            'category':'Pentest',
            'syntax_examples':['dps_uid_gen %f%l@acme.corp acme.corp.employees.txt # first and last initial','dps_uid_gen %F%l@acme.corp acme.corp.employees.txt # first name and last initial','dps_uid_gen %f%L@acme.corp acme.corp.employees.txt # first initial and last name'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_www_commentscrape':
        {'title':'DPS->WWW->Comment Scrape',
            'desc':'Scrape a Web Page for HTML and JS Comments.',
            'args':['(URL)'],
            'category':'Pentest-WWW',
            'syntax_examples':['dps_www_commentscrape https://www.rackunsec.org/'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_www_verbs':
        {'title':'DPS->WWW->Verb Test',
            'desc':'Test web service for acceptable HTTP Verbs.',
            'args':['(URL)'],
            'category':'Pentest-WWW',
            'syntax_examples':['dps_www_verbs https://www.rackunsec.org/'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_wifi':
        {'title':'DPS Wi-Fi Monitor Mode',
            'desc':'Set a wireless device into RFMON mode with a single command.',
            'args':['(Wi-Fi device name)'],
            'category':'Pentest-Wi-Fi',
            'syntax_examples':['dps_wifi --monitor wlan0','dps_wifi --mac 00:11:22:33:44:55','dps_wifi --managed wlan0'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    'dps_config':
        {'title':'DPS Configuration Settings',
            'desc':'Set configuration settings for your own sessions. This will update the local ~/.dps/config/dps.ini file with your arguments.',
            'args':['prompt (0-9)','--show','--update-net'],
            'category':'System',
            'syntax_examples':['dps_config prompt 5 # set current theme to 5', 'dps_config --show # show current theme', 'dps_config --update-net # get an ip address'],
            'author':{'name':'RackunSec','url':'https://github.com/RackunSec/'}
        },
    ## Do not delete below, that is a template for adding commands:
    #'name':
    #    {'title':'',
    #        'desc':'',
    #        'args':[],
    #        'syntax_examples':[]
    #    },
}

## ------------------------------------------------
## DO NOT EDIT BELOW THIS LINE:
##-------------------------------------------------

## Method: Show help dialog:
def msg(cmd_name,session,prompt_ui):
    WARN=prompt_ui.bcolors['YELL']
    BUNDER=prompt_ui.bcolors['BUNDER']
    ENDC=prompt_ui.bcolors['ENDC']
    BOLD=prompt_ui.bcolors['BOLD']
    CMT=prompt_ui.bcolors['COMMENT']
    if cmd_name != "":
        if cmd_name in modules_list:
            dialog=modules_list[cmd_name]
            print(f"\n{BOLD}▾ {dialog['title']} ▾ {ENDC}")
            print(f"{dialog['desc']}\n")
            print(f"{BUNDER}Command Arguments{ENDC}\n ▹ {WARN}{cmd_name}{ENDC}",end=" ")
            for arg in dialog['args']:
                print(f"{arg}",end=" ")
            print(f"\n\n{BUNDER}Command Syntax{ENDC}")
            for syntax in dialog['syntax_examples']:
                syntax_cmd = syntax.split(" ",1)[0] # drop off any args
                if len(syntax.split())>1:
                    syntax_args = syntax.split(" ",1)[1] # drop off command
                    syntax_comment = syntax_args.split("#")
                    if len(syntax_comment)>1:
                        syntax_args = syntax_comment[0]+CMT+"#"+syntax_comment[1]+ENDC
                else:
                    syntax_args = ""
                print(f" ▹ {WARN}{syntax_cmd}{ENDC} {syntax_args}")
            print(f"\n{BUNDER}Author{ENDC}\n ▹ {dialog['author']['name']} ({dialog['author']['url']})\n")
        else:
            print(f"{WARN}[{BOLD}?{ENDC}{WARN}] No help dialog for {BOLD}\"{cmd_name}\"{ENDC}{WARN} yet.\n    Please create one in the dps_help Python module.{ENDC}")
            return
        return
    else:
        print(f"\n{BOLD}The Demon Pentest Shell (Version: {session.VERSION}){ENDC}")
        print(f"\n ▿ {BOLD}[ Built In Commands ]{ENDC} ▿ ")
        print (f"  ◦ {WARN}help{ENDC} - this cruft.")
        print (f"  ◦ {WARN}exit/quit/CTRL+D{ENDC} - return to terminal OS shell.")
        for cat in modules_categories:
            print(f"\n ▿ {BOLD}[ {cat} ]{ENDC} ▿ ")
            for module in modules_list:
                if(modules_list[module]['category'] == cat):
                    #dialog=modules_list[module]
                    print (f"  ◦ {WARN}{module}{ENDC} - {modules_list[module]['title']}")

        print(f"\n ▿ {BOLD}[ Keyboard Shortcuts ] {ENDC} ▿ ")
        print(f"  ◦ {WARN}CTRL+R{ENDC} - Search command history.")
        print(f"  ◦ {WARN}CTRL+A{ENDC} - Move cursor to beginning of line (similar to \"HOME\" key).")
        print(f"  ◦ {WARN}CTRL+P{ENDC} - Place the previously ran command into the command line.")
        print(f"  ◦ {WARN}CTRL+B{ENDC} - Move one character before cursor.")
        print(f"  ◦ {WARN}ALT+F{ENDC} -  Move one character forward.")
        print(f"  ◦ {WARN}CTRL+C{ENDC} - Kill current process.\n")
