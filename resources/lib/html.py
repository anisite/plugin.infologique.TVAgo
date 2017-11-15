# -*- coding: utf-8 -*-

# version 3.0.0 - By CB
# version 2.0.2 - By SlySen
# version 0.2.6 - By CB

import re
import socket, xbmc, xbmcaddon
from StringIO import StringIO
import urllib2, gzip



# Merci à l'auteur de cette fonction
def unescape_callback(matches):
    """ function docstring """
    html_entities = \
    {
        'quot':'\"', 'amp':'&', 'apos':'\'', 'lt':'<',
        'gt':'>', 'nbsp':' ', 'copy':'©', 'reg':'®',
        'Agrave':'À', 'Aacute':'Á', 'Acirc':'Â',
        'Atilde':'Ã', 'Auml':'Ä', 'Aring':'Å',
        'AElig':'Æ', 'Ccedil':'Ç', 'Egrave':'È',
        'Eacute':'É', 'Ecirc':'Ê', 'Euml':'Ë',
        'Igrave':'Ì', 'Iacute':'Í', 'Icirc':'Î',
        'Iuml':'Ï', 'ETH':'Ð', 'Ntilde':'Ñ',
        'Ograve':'Ò', 'Oacute':'Ó', 'Ocirc':'Ô',
        'Otilde':'Õ', 'Ouml':'Ö', 'Oslash':'Ø',
        'Ugrave':'Ù', 'Uacute':'Ú', 'Ucirc':'Û',
        'Uuml':'Ü', 'Yacute':'Ý', 'agrave':'à',
        'aacute':'á', 'acirc':'â', 'atilde':'ã',
        'auml':'ä', 'aring':'å', 'aelig':'æ',
        'ccedil':'ç', 'egrave':'è', 'eacute':'é',
        'ecirc':'ê', 'euml':'ë', 'igrave':'ì',
        'iacute':'í', 'icirc':'î', 'iuml':'ï',
        'eth':'ð', 'ntilde':'ñ', 'ograve':'ò',
        'oacute':'ó', 'ocirc':'ô', 'otilde':'õ',
        'ouml':'ö', 'oslash':'ø', 'ugrave':'ù',
        'uacute':'ú', 'ucirc':'û', 'uuml':'ü',
        'yacute':'ý', 'yuml':'ÿ'
    }

    entity = matches.group(0)
    val = matches.group(1)

    try:
        if entity[:2] == r'\u':
            return entity.decode('unicode-escape')
        elif entity[:3] == '&#x':
            return unichr(int(val, 16))
        elif entity[:2] == '&#':
            return unichr(int(val))
        else:
            return html_entities[val].decode('utf-8')

    except (ValueError, KeyError):
        pass

def html_unescape(data):
    """ function docstring """
    data = data.decode('utf-8')
    data = re.sub(r'&#?x?(\w+);|\\\\u\d{4}', unescape_callback, data)
    data = data.encode('utf-8')
    return data

def get_url_txt(the_url, enablePK=False):
    """ function docstring """
    log("--get_url_txt----START--")
    
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
    log("--encoding--")
    log(response.info().get('Content-Encoding'))
    
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read() )
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data = response.read()
    
    response.close()
    
    log("--data--")
    #log(data)
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
