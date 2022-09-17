# -*- coding: utf-8 -*-

# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB

import sys, re
import socket, xbmc, xbmcaddon, simplejson
import gzip

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import unquote, quote_plus, unquote_plus, urljoin, urlparse
    from urllib.request import Request, urlopen
    from io import StringIO as StringIO
else:
    # Python 2 stuff
    from urlparse import urljoin, urlparse
    from urllib import quote_plus, unquote_plus, unquote
    from urllib2 import Request, urlopen
    from StringIO import StringIO

def handleHttpResponse(response):

    if sys.version_info.major >= 3:
        if response.info().get('Content-Encoding') == 'gzip':
            f = gzip.GzipFile(fileobj=response)
            data = f.read()
            return data
        else:
            data = response.read()
            return data
    else:
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO( response.read() )
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            return data
        else:
            return response.read()

def get_policykey(account, player, embed):
    #
    #5813221784001
    #sd748Ih4e
    #default
    #
    POLICY_CACHE_URL = "https://players.brightcove.net/" + account + "/" + player + "_" + embed + "/config.json"
    
    load = simplejson.loads(get_url_txt(POLICY_CACHE_URL, False))
    log(load["video_cloud"]["policy_key"])

    return load["video_cloud"]["policy_key"]

def get_url_txt(the_url, enablePK=False):
    """ function docstring """
    log("html.get_url_txt")

    req = Request(the_url)
    req.add_header(\
                   'User-Agent', \
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'\
                   )
    if enablePK:
        req.add_header('Accept', 'application/json;pk=' + xbmcaddon.Addon().getSetting('policyKey'))
    else:
        req.add_header('Accept', 'application/json')
    req.add_header('Accept-Language', 'fr-CA,fr-FR;q=0.8,en-US;q=0.6,fr;q=0.4,en;q=0.2')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Connection', 'keep-alive')
    req.add_header('Pragma', 'no-cache')
    req.add_header('Cache-Control', 'no-cache')
    response = urlopen(req)

    data = handleHttpResponse(response)

    log("html.get_url_txtExit")
    return data

def is_network_available(url):
    """ function docstring """
    try:
        # see if we can resolve the host name -- tells us if there is a DNS listening
        host = socket.gethostbyname(url)
        # connect to the host -- tells us if the host is actually reachable
        srvcon = socket.create_connection((host, 80), 2)
        srvcon.close()
        return True
    except socket.error:
        return False

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
