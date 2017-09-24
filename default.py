# -*- coding: utf-8 -*-

import os, urllib, sys, traceback, xbmcplugin, xbmcaddon, xbmc, simplejson, xbmcgui

from BeautifulSoup import BeautifulSoup
from resources.lib import content, parse, navig

def peupler():
    if filtres['content']['mediaBundleId']>0:
        creer_liste_videos()
    elif filtres['content']['genreId']!='':
        creer_liste_filtree()
    else:
        creer_menu_categories()

def creer_menu_categories():
    """ function docstring """
    navig.ajouterItemAuMenu(content.dictOfMainDirs(filtres))
    navig.ajouterItemAuMenu(content.dictOfGenres(filtres))
    xbmc.executebuiltin('Container.SetViewMode(500)') # "Info-wall" view. 

def creer_liste_filtree():
    """ function docstring """
    log("---creer_liste_filtree--START----")
    log(filtres['content']['url'])
    if "saisons" in filtres['content']['url'] :
        navig.ajouterItemAuMenu(content.loadEmission(filtres))
    else:
        navig.ajouterItemAuMenu(content.loadListeSaison(filtres))
    xbmc.executebuiltin('Container.SetViewMode(55)') # "Info-wall" view. 


def creer_liste_videos():
    """ function docstring """
    log("---creer_liste_videos--START----")
    navig.ajouterItemAuMenu(parse.ListeVideosGroupees(filtres))

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

def set_content(content):
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
log('--- init -----------------')
# ---

PARAMS = get_params()

URL = None
MODE = None
SOURCE_URL = ''
FILTERS = ''
filtres = {}

try:
    URL = urllib.unquote_plus(PARAMS["url"])
    log("PARAMS['url']:"+URL)
except StandardError:
    pass
try:
    MODE = int(PARAMS["mode"])
    log("PARAMS['mode']:"+str(MODE))
except StandardError:
    pass
try:
    FILTERS = urllib.unquote_plus(PARAMS["filters"])
except StandardError:
    FILTERS = content.FILTRES
try:
    SOURCE_URL = urllib.unquote_plus(PARAMS["sourceUrl"])
except StandardError:
    pass

filtres = simplejson.loads(FILTERS)
   
if SOURCE_URL !='':
    navig.jouer_video(SOURCE_URL)

elif MODE == 99:
    ADDON.openSettings()
    
else:
    peupler()
    set_content('episodes')


if MODE is not 99:
    #set_sorting_methods(MODE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if MODE is not 4 and xbmcaddon.Addon().getSetting('DeleteTempFiFilesEnabled') == 'true':
    PATH = xbmc.translatePath('special://temp').decode('utf-8')
    FILENAMES = next(os.walk(PATH))[2]
    for i in FILENAMES:
        if ".fi" in i:
            os.remove(os.path.join(PATH, i))