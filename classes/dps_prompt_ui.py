### UI STUFF: (This needs to be here because we don't know the install path yet.)
class prompt_ui:
    bcolors = {
        'OKGREEN' : '\033[3m\033[92m ✔ ',
        'FAIL' : '\033[3m\033[91m ✖ ',
        'ENDC' : '\033[0m',
        'BOLD' : '\033[1m',
        'YELL' : '\033[33m\033[3m',
        'ITAL' : '\033[3m',
        'UNDER' : '\033[4m',
        'BLUE' : '\033[34m',
        'BUNDER': '\033[1m\033[4m',
        'WARN': '\033[33m\033[3m ⚑ ',
        'COMMENT': '\033[37m\033[3m',
    }
    dps_themes = {
        0 : 'DPS',
        1 : 'PIRATE',
        2 : 'BONEYARD',
        3 : '1980S',
        5 : 'Nouveau',
        6 : 'Daemo',
        7 : 'Dropped'
    }
