# -*- coding: utf-8 -*-

# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB

import re
import socket, xbmc, xbmcaddon
from StringIO import StringIO
import urllib2, gzip

def get_url_txt(the_url, enablePK=False):
    """ function docstring """
    log("html.get_url_txt")

    req = urllib2.Request(the_url)
    req.add_header(\
                   'User-Agent', \
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'\
                   )
    if enablePK:
        req.add_header('Accept', 'application/json;pk='+ xbmcaddon.Addon().getSetting('policyKey') )
    else:
        req.add_header('Accept', 'application/json')
    req.add_header('Accept-Language', 'fr-CA,fr-FR;q=0.8,en-US;q=0.6,fr;q=0.4,en;q=0.2')
    req.add_header('Accept-Encoding', 'gzip, deflate')
    req.add_header('Connection', 'keep-alive')
    req.add_header('Pragma', 'no-cache')
    req.add_header('Cache-Control', 'no-cache')
    response = urllib2.urlopen(req)

    data = ""

    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read() )
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()

    response.close()

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
