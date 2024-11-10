LOGDEBUG = 0
LOGNOTICE = 1
LOGWARNING = 2
LOGERROR = 3
LOGSEVERE = 4

MODEMOCK = 1

def log(message, level=LOGDEBUG):
    print(f"LOG [{level}]: {message}")

def translatePath(path):
    return path

def getInfoLabel(path):
    return "21.1"
