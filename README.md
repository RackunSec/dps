# Demon Pentest Shell
A simple shell wrapper for superior logging capabilities. All commands are logged to ```~/log_dps_history.csv``` with with time,hostname,network:ip,who,command.

This project requires Python3 and the following Python modules,
* os
* subprocess
* sys
* re
* cmd2
* ifaddr
* socket
* getpass
* datetime
## The Shell
```
root@kali:/opt/dps# python3 dps.py 

 *** Welcome to the Demon Pentest Shell
 *** hit CTRL+D to exit to standard shell.
 *** type cmd <command> to run basic shell commands.

root@kali [/opt/dps] >>
```
## Example Log Output
```
Date,Hostname,Network,Who,Where,Command
2020-04-08 16:30:13.219498,kali,eth0:192.168.44.140,root,/opt/dps,ls 
2020-04-08 16:30:17.141034,kali,eth0:192.168.44.140,root,/opt/dps,cd "this new/"
2020-04-08 16:30:17.688497,kali,eth0:192.168.44.140,root,/opt/dps/this new,ls 
2020-04-08 16:30:19.093417,kali,eth0:192.168.44.140,root,/opt/dps/this new,cd test
2020-04-08 16:30:20.588323,kali,eth0:192.168.44.140,root,/opt/dps/this new/test,ls 
2020-04-08 16:30:25.399867,kali,eth0:192.168.44.140,root,/opt/dps/this new/test,touch file.txt
2020-04-08 16:30:26.505094,kali,eth0:192.168.44.140,root,/opt/dps/this new/test,ls 
2020-04-08 16:30:28.711438,kali,eth0:192.168.44.140,root,/opt/dps/this new/test,cat file.txt
```
## Shiny Features
Because this is built with Cmd2, the shell has a lot of great built-in features. 
* Use the up and down arrows to scroll through history
* Use CTRL+R to do a reverse history search lookup
* Use pipes for stdout, stderr just like you would in a native shell
* Easily create "command modules"

## Command modules
* ```x```: use this for tab-autocompletion of file system paths
* ```exit```: use this, or ```quit``` or ```CTRL+D``` to exit DPS

## Installation
To install DPS, simply install the requirements using pip3 and copy the ```dps.py``` into your ```$PATH``` like ```/usr/local/bin```, etc:
```
root@kali:~# cd /tmp
root@kali:/tmp# git clone https://github.com/weaknetlabs/dps.git
root@kali:/tmp# cd dps
root@kali:/tmp/dps# pip3 install -r requirements.txt
root@kali:/tmp/dps# cp dps.py /usr/local/bin/
root@kali:/tmp/dps# dps.py
```
