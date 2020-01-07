# -*- coding: utf-8 -*-

import sys, urllib, xbmcgui, xbmcplugin, xbmcaddon, re, cache, simplejson, xbmc, html, m3u8, inputstreamhelper

ADDON = xbmcaddon.Addon()
ADDON_IMAGES_BASEPATH = ADDON.getAddonInfo('path')+'/resources/media/images/'
ADDON_FANART = ADDON.getAddonInfo('path')+'/fanart.jpg'
THEPLATFORM_CONTENT_URL = "https://edge.api.brightcove.com/playback/v1/accounts/5481942443001/videos/"
ADDON_PREFERRED_RESOLUTION = ADDON.getSetting('PreferedResolution')
ADDON_PREFERRED_BITRATE = ADDON.getSetting('PreferedBitrate')

__handle__ = int(sys.argv[1])

class stream():
  def __init__(self, strUri, nBitrate, nHRes, nVRes):
    self.strUri = strUri
    self.nBitrate = nBitrate
    self.nHRes = nHRes
    self.nVRes = nVRes
    self.strLicUri = ""
    self.strDrm = ""
    self.strProtocol = ""

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

    uri = None

    strURL = THEPLATFORM_CONTENT_URL + source_url
    log("Accessing: " + strURL)

    # Do not use cache or live tv will not work
    jsonData = simplejson.loads(html.get_url_txt(strURL, True))

    log("Returned: ")
    log(jsonData)

    streams = []

    for source in jsonData['sources']:
        if 'src' in source:
            if 'type' in source:
                if source['type'] == "application/dash+xml":
                    nBitrate = 10000;
                    nHRes = 1920;
                    nVRes = 1080;
                    aStream = stream(source['src'], nBitrate, nHRes, nVRes)
                    aStream.strProtocol = "mpd";
                    if 'key_systems' in source:
                        keySystems = source['key_systems'];
                        if 'com.widevine.alpha' in keySystems:
                            aStream.strDrm = "com.widevine.alpha";
                            if 'license_url' in keySystems['com.widevine.alpha']:
                                aStream.strLicUri = keySystems['com.widevine.alpha']['license_url'];
                        elif 'widevine' in keySystems:
                            aStream.strDrm = "widevine";
                            if 'license_url' in keySystems['widevine']:
                                aStream.strLicUri = keySystems['widevine']['license_url'];
                    streams.append(aStream)
                elif source['type'] == "application/x-mpegURL":
                    log("Unsupported stream")
                    # nBitrate = 10000;
                    # nHRes = 1920;
                    # nVRes = 1080;
                    # aStream = stream(source['src'], nBitrate, nHRes, nVRes)
                    # aStream.strProtocol = "hls";
                    # streams.append(aStream)
                elif "master.m3u8" in source['src']:
                    variant_m3u8 = m3u8.loads(html.get_url_txt(source['src'], True))
                    for playlist in variant_m3u8.playlists:
                        nBitrate = 0;
                        nHRes = 0;
                        nVRes = 0;
                        if playlist.stream_info.bandwidth:
                            nBitrate = playlist.stream_info.bandwidth
                        if playlist.stream_info.resolution and len(playlist.stream_info.resolution) == 2:
                            nHRes = playlist.stream_info.resolution[0];
                            nVRes = playlist.stream_info.resolution[1];
                        if source['type'] == "application/vnd.apple.mpegurl":
                            pUri = playlist.uri.split('?', 2)[0] + "?" + source['src'].split('?', 2)[1]
                        else:
                            pUri = playlist.uri
                        aStream = stream(pUri, nBitrate, nHRes, nVRes)
                        streams.append(aStream)
            else:
                # Direct streams (MP4)
                nBitrate = 0;
                nHRes = 0;
                nVRes = 0;
                if 'avg_bitrate' in source:
                    nBitrate = source['avg_bitrate'];
                if 'width' in source:
                    nHRes = source['width'];
                if 'height' in source:
                    nVRes = source['height'];
                aStream = stream(source['src'], nBitrate, nHRes, nVRes)
                streams.append(aStream)

    nHResPreferred = 0;
    if ADDON_PREFERRED_RESOLUTION == "1":
        nHResPreferred = 1920;
    elif ADDON_PREFERRED_RESOLUTION == "2":
        nHResPreferred = 1280;
    elif ADDON_PREFERRED_RESOLUTION == "3":
        nHResPreferred = 960;
    elif ADDON_PREFERRED_RESOLUTION == "4":
        nHResPreferred = 640;
    elif ADDON_PREFERRED_RESOLUTION == "5":
        nHResPreferred = 480;

    # Sort the streams by resolution closest to preferred
    streams.sort(key=lambda x: abs(x.nHRes - nHResPreferred))
    
    # Temporarily select a stream with the right resolution
    selectedStream = None
    if len(streams) > 0:
        if ADDON_PREFERRED_RESOLUTION == "0":
            selectedStream = streams[len(streams) - 1];
        else:
            selectedStream = streams[0]

    if len(streams) > 0:
        # Keep the streams with the same resolution
        sameRes = [x for x in streams if x.nHRes == selectedStream.nHRes]
        # Sort then by bitrate
        sameRes.sort(key=lambda x: x.nBitrate)
        # Take the highest or the lowest
        if ADDON_PREFERRED_BITRATE == "0":
            selectedStream = sameRes[len(sameRes) - 1];
        else:
            selectedStream = sameRes[0];

    # Start the stream
    if selectedStream and selectedStream.strUri:
        log("bitrate: " + str(selectedStream.nBitrate))
        log("resolution: " + str(selectedStream.nHRes) + "x" + str(selectedStream.nVRes))
        log("src: " + selectedStream.strUri)
        log("lic_uri: " + selectedStream.strLicUri)
        log("drm: " + selectedStream.strDrm)
        log("protocol: " + selectedStream.strProtocol)
        if selectedStream.strProtocol != "":
            is_helper = inputstreamhelper.Helper(selectedStream.strProtocol, drm=selectedStream.strDrm)
            if is_helper.check_inputstream():
                playitem = xbmcgui.ListItem(path=selectedStream.strUri)
                playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                playitem.setProperty('inputstream.adaptive.manifest_type', selectedStream.strProtocol)
                playitem.setProperty('inputstream.adaptive.license_type', selectedStream.strDrm)
                playitem.setProperty('inputstream.adaptive.license_key', selectedStream.strLicUri + '||R{SSM}|')
                xbmcplugin.setResolvedUrl(__handle__, True, playitem)
        else:
            play_item = xbmcgui.ListItem(path=selectedStream.strUri)
        xbmcplugin.setResolvedUrl(__handle__, True, play_item)
    else:
        xbmc.executebuiltin('Notification(%s,Unable to get video URL,5000,%s')

    log("navig.PlayVideoExit")

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