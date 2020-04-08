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
root@demon2:~/Code# ./dps.py 
 *** Welcome to the Demon Pentest Shell
 *** hit CTRL+D to exit to standard shell.
 *** type cmd <command> to run basic shell commands.

dps> 
```
## Example Log Output
```
Date,Hostname,Network,Who,Command
2020-04-07 21:52:34.516429,demon2.4,ens33:192.168.159.132,root,ifconfig
2020-04-07 21:52:39.497779,demon2.4,ens33:192.168.159.132,root,ls -lah
2020-04-07 21:52:48.911536,demon2.4,ens33:192.168.159.132,root,iw dev
2020-04-07 21:53:16.428270,demon2.4,ens33:192.168.159.132,root,top
2020-04-07 22:11:51.024047,demon2.4,ens33:192.168.159.132,root,ifconfig
2020-04-07 22:15:04.322567,demon2.4,ens33:192.168.159.132,root,nmap localhost
2020-04-07 22:15:28.055986,demon2.4,ens33:192.168.159.132,root,wc -l /root/Code/dps.py
2020-04-07 22:15:39.899211,demon2.4,ens33:192.168.159.132,root,cat ~/.log_dps_history.csv
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
