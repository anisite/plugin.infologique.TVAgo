# -*- coding: utf-8 -*-

import os, sys, traceback, xbmcplugin, xbmcaddon, xbmc, simplejson, xbmcgui

from resources.lib import content, navig

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import quote_plus, unquote_plus, unquote
else:
    # Python 2 stuff
    from urllib import quote_plus, unquote_plus, unquote

def Load():
    log("default.Load")
    if filtres['content']['genreId'] != '':
        CreateFilteredList()
    else:
        CreateMainMenu()
    log("default.LoadExit")

def CreateMainMenu():
    """ function docstring """
    log("default.CreateMainMenu")
    navig.AddItemInMenu(content.LoadMainMenu(filtres))
    xbmc.executebuiltin('Container.SetViewMode(50)') # "List" view.
    log("default.CreateMainMenuExit")

def CreateFilteredList():
    """ function docstring """
    log("default.CreateFilteredList")
    log(filtres['content']['url'])
    if 'containerId' in filtres['content']:
        log(filtres['content']['containerId'])
        navig.AddItemInMenu(content.LoadContainerItems(filtres))
    else:
        navig.AddItemInMenu(content.LoadContainers(filtres))
    xbmc.executebuiltin('Container.SetViewMode(50)') # "List" view.
    log("default.CreateFilteredListExit")

def get_params():
    """ function docstring """
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params)-1] == '/':
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for k in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[k].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

def SetContent(content):
    """ function docstring """
    xbmcplugin.setContent(int(sys.argv[1]), content)
    return

def set_sorting_methods(mode):
    pass
    #if xbmcaddon.Addon().getSetting('SortMethodTvShow') == '1':
    #    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    #    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)
    #return

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))


# ---
log('--- Addon Entry ---')
# ---

PARAMS = get_params()

URL = None
MODE = None
SOURCE_URL = ''
FILTERS = ''
filtres = {}

try:
    URL = unquote_plus(PARAMS["url"])
    log("PARAMS['url']:" + URL)
except Exception:
    pass
try:
    MODE = int(PARAMS["mode"])
    log("PARAMS['mode']:" + str(MODE))
except Exception:
    pass
try:
    FILTERS = unquote_plus(PARAMS["filters"])
except Exception:
    FILTERS = content.FILTRES
try:
    SOURCE_URL = unquote_plus(PARAMS["sourceUrl"])
except Exception:
    pass

filtres = simplejson.loads(FILTERS)

if SOURCE_URL !='':
    navig.PlayVideo(SOURCE_URL)

elif MODE == 99:
    ADDON.openSettings()

else:
    Load()
    SetContent('episodes')


if MODE != 99:
    #set_sorting_methods(MODE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if MODE != 4 and xbmcaddon.Addon().getSetting('DeleteTempFiFilesEnabled') == 'true':
    PATH = xbmc.translatePath('special://temp').decode('utf-8')
    FILENAMES = next(os.walk(PATH))[2]
    for i in FILENAMES:
        if ".fi" in i:
            os.remove(os.path.join(PATH, i))