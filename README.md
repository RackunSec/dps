# Demon Pentest Shell
A simple shell wrapper for superior logging capabilities. All commands are logged to ```~/log_dps_history.csv``` with with time,hostname,network:ip,who,command.

This project requires Python3 and the following Python modules,
* readline
* os # for the commands, of course. These will be passed ot the shell.
* sys # for exit
* re # regexps
* ifaddr # NIC info
* socket # for HOSTNAME
* getpass # for logging the username
* datetime # for logging the datetime

## The Shell
```
root@demon2:~/Code/dps# ./dps.py 

 *** Welcome to the Demon Pentest Shell
 *** hit CTRL+D to exit to standard shell.
 *** type cmd <command> to run basic shell commands.

root@demon2.4[/root/Code/dps]>> ls
dps.py  README.md  requirements.txt
root@demon2.4[/root/Code/dps]>> 
```
## Example Log Output
```
root@demon2:~/Code/dps# cat ~/.log_dps_history.csv 
When,Host,Network,Who,Where,What
2020-04-14 07:56:52.412353,demon2.4,ens33:192.168.159.132,root,/root/Code/dps,ls
2020-04-14 07:56:53.177506,demon2.4,ens33:192.168.159.132,root,/root/Code/dps,cd
2020-04-14 07:56:53.641559,demon2.4,ens33:192.168.159.132,root,/root,ls
2020-04-14 07:56:56.756188,demon2.4,ens33:192.168.159.132,root,/root,cd Penetration Testing
2020-04-14 07:56:58.374275,demon2.4,ens33:192.168.159.132,root,/root/Penetration Testing,ls
2020-04-14 07:57:00.117010,demon2.4,ens33:192.168.159.132,root,/root/Penetration Testing,cd Clients
2020-04-14 07:57:00.389277,demon2.4,ens33:192.168.159.132,root,/root/Penetration Testing/Clients,ls
2020-04-14 07:57:18.294996,demon2.4,ens33:192.168.159.132,root,/root/Penetration Testing/Clients,ifconfig | grep inet
2020-04-14 07:57:31.235330,demon2.4,ens33:192.168.159.132,root,/root/Penetration Testing/Clients,exit
root@demon2:~/Code/dps#
```
## Shiny Features
Because this is built with readline, the shell has a lot of great built-in features. 
* Use the up and down arrows to scroll through history
* Use CTRL+R to do a reverse history search lookup
* Use pipes for stdout, stderr just like you would in a native shell

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
