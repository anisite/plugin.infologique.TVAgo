# -*- coding: utf-8 -*-

import sys, urllib, xbmcgui, xbmcplugin, xbmcaddon, re, cache, simplejson, xbmc, html
from BeautifulSoup import BeautifulSoup

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'
THEPLATFORM_CONTENT_URL = "https://edge.api.brightcove.com/playback/v1/accounts/5481942443001/videos/"

__handle__ = int(sys.argv[1])

def AddItemInMenu(items):
    for item in items:
        if item['isDir'] == True:
            AddFolder(item)
        else:
            AddVideo(item)

    if items:
        if items[0]['sortable']  :
            xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
            xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_DATE)

def AddFolder(show):

    strTitle = show['title']
    strURL = show['url']
    strImage =show['image']
    strPlot = remove_any_html_tags(show['plot'])
    strFanart = show['fanart']
    filtres = show['filtres']

    if strPlot=='':
        strPlot = urllib.unquote(ADDON.getAddonInfo('id') + ' v.' + ADDON.getAddonInfo('version'))
    if ADDON.getSetting('EmissionNameInPlotEnabled') == 'true':
        strPlot = '[B]' + strTitle + '[/B][CR]' + urllib.unquote(strPlot)
    if strImage=='':
        strImage = ADDON_IMAGES_BASEPATH+'default-folder.png'

    """ function docstring """
    entry_url = sys.argv[0] + "?url=" + strURL + "&mode=1" + "&filters=" + urllib.quote(simplejson.dumps(filtres))

    bResult = True
    liz = xbmcgui.ListItem(strTitle, iconImage=strImage, thumbnailImage=strImage)

    liz.setInfo(\
        type="video",\
        infoLabels={\
            "title": strTitle,\
            "plot": strPlot
        }\
    )
    SetFanart(liz, strFanart)

    bResult = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=True)

    return bResult

def SetFanart(liz,fanart):
    if ADDON.getSetting('FanartEnabled') == 'true':
        if ADDON.getSetting('FanartEmissionsEnabled') == 'true':
            liz.setProperty('fanart_image', fanart)
        else:
            liz.setProperty('fanart_image', ADDON_FANART)


def AddVideo(show):
    strTitle = show['title']
    strURL = show['url']
    strImage = show['image']

    strPlot = show['plot']
    strDuration = show['duration']
    strFanart = show['fanart']
    strSourceUrl = show['sourceUrl']
    strPremiere = show['startDate']
    strGenre = show['genre']
    strRating = show['rating']

    bResult = True
    entry_url = sys.argv[0] + "?url=" + urllib.quote_plus(strURL) + "&sourceUrl=" + urllib.quote_plus(strSourceUrl)

    liz = xbmcgui.ListItem(remove_any_html_tags(strTitle), iconImage=ADDON_IMAGES_BASEPATH+"default-video.png", thumbnailImage=strImage)
    liz.setInfo(\
        type="video",\
        infoLabels={\
            "title":remove_any_html_tags(strTitle),\
            "plot":remove_any_html_tags(strPlot, False),\
            "duration":strDuration,\
            "premiered":strPremiere,\
            "genre":strGenre,\
            "mpaa":strRating}\
    )
    liz.addContextMenuItems([('Informations', 'Action(Info)')])
    SetFanart(liz, strFanart)
    liz.setProperty('IsPlayable', 'true')

    bResult = xbmcplugin.addDirectoryItem(handle=__handle__, url=entry_url, listitem=liz, isFolder=False)
    return bResult

RE_HTML_TAGS = re.compile(r'<[^>]+>')
RE_AFTER_CR = re.compile(r'\n.*')

def PlayVideo(source_url):
    """ function docstring """
    log("navig.PlayVideo")
    check_for_internet_connection()
    uri = None

    strURL = THEPLATFORM_CONTENT_URL + source_url
    log("Accessing: " + strURL)

    # Do not use cache or live tv will not work
    jsonData = simplejson.loads(html.get_url_txt(strURL, True))

    log("Returned: ")
    log(jsonData)

    strSrcUrl = ""
    strBackSrcUrl = ""

    for x in jsonData['sources']:
        #log(x)

        # TBD Preferred stream in settings
        try:
            if x['ext_x_version'] == "5":
                strSrcUrl = x['src']
                break
            if x['height'] == 1080:
                strSrcUrl = x['src']
                break
        except KeyError:
            strBackSrcUrl = x['src']

    if strSrcUrl:
        uri = strSrcUrl
    else:
        uri = strBackSrcUrl

    log("src: " + uri)

    # Start the stream
    if uri:
        play_item = xbmcgui.ListItem(path=uri)
        xbmcplugin.setResolvedUrl(__handle__, True, play_item)
    else:
        xbmc.executebuiltin('Notification(%s,Unable to get video URL,5000,%s')

    log("navig.PlayVideoExit")

def check_for_internet_connection():
    """ function docstring """
    if ADDON.getSetting('NetworkDetection') == 'false':
        return
    return

def remove_any_html_tags(text, crlf=True):
    """ function docstring """
    text = RE_HTML_TAGS.sub('', text)
    text = text.lstrip()
    if crlf == True:
        text = RE_AFTER_CR.sub('', text)
    return text

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))