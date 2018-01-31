# -*- coding: utf-8 -*-
# encoding=utf8

import urllib2, cache, re, xbmcaddon, html, xbmc, datetime, time, copy
import simplejson as json
import xml.etree.ElementTree as ET
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup, Tag, NavigableString

BASE_URL = 'https://viamw-android-adapter.viago.io'
MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

SEASON = 'Saison'
EPISODE = 'Episode'
LABEL = 'label'
FILTRES = '{"content":{"genreId":"","mediaBundleId":-1,"afficherTous":false},"show":{"' + SEASON + '":"","' + EPISODE + '":"","' + LABEL + '":""},"fullNameItems":[],"sourceId":""}'
INTEGRAL = 'Integral'

def GetCopy(item):
    return copy.deepcopy(item)

def u(data):
    return data.encode('utf-8') #.decode('string_escape').decode('utf8')

def LoadItems(filtres):
    log("content.LoadItems")
    log(filtres)

    strURL = BASE_URL + "/page/"+ filtres['content']['url'] +"?uuid=5a0f10e5f31d1a2&gid=&appId=5955fc5423eec60006c951ef&locale=en"
    log("Accessing: " + strURL)
    jsonData = json.loads(cache.get_cached_content(strURL), encoding='utf-8')
    log("Returned:")
    log(jsonData)

    jsonSections = jsonData['item']

    listItems = []
    for jsonSection in jsonSections :
        log(jsonSection['attributes'])
        dict = {}
        for s in jsonSection['attributes']:
            dict[s['key']] = s['value']

        listItems = listItems + AddItemToList(jsonSection, dict, filtres)

    log("content.LoadItemsExit")
    return listItems

def AddItemToList(jsonSection,infoDict,filtres):
    listItems = []

    # External uri item
    if u(jsonSection['typeId']) == "go-item-external-uri":
        log("content.AddItemToList: Skipping externalUri item: " + infoDict['externalUri'])

    # Video or Clip item
    if u(jsonSection['typeId']) == "go-item-video" or \
       u(jsonSection['typeId']) == "go-item-clip":

        url = infoDict['assetId']

        newItem = {   'genreId': 1,
                      'title': urllib2.unquote(u(infoDict['title'])),
                      'sourceUrl' : url,
                      'filtres' : GetCopy(filtres)
                  }

        newItem['url'] = "url"

        if 'description' in infoDict:
            newItem['plot'] = u(infoDict['description'])
        elif 'shortDescription' in infoDict:
            newItem['plot'] = u(infoDict['shortDescription'])
        else:
            newItem['plot'] = ""

        if 'image-background' in infoDict:
            newItem['image'] = infoDict['image-background']
        else:
            newItem['image'] = xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'

        if 'genre' in infoDict:
            newItem['genre'] = infoDict['genre']
        else:
            newItem['genre'] = ""

        if 'publishedDate' in infoDict:
            newItem['startDate'] = datetime.datetime.fromtimestamp(int(infoDict['publishedDate']) / 1000).strftime('%Y-%m-%d')
        elif 'availableDate' in infoDict:
            newItem['startDate'] = datetime.datetime.fromtimestamp(int(infoDict['availableDate']) / 1000).strftime('%Y-%m-%d')
        else:
            newItem['startDate'] = None

        # Live item should not have a start date
        if 'live' in infoDict:
            newItem['startDate'] = None

        if 'parentalRating' in infoDict:
            newItem['rating'] = infoDict['parentalRating']
        else:
            newItem['rating'] = ""

        newItem['duration'] = int(infoDict['video-duration']) / 1000

        newItem['fanart'] = None

        newItem['filtres']['content']['genreId'] = newItem['genreId']
        newItem['filtres']['content']['url'] = url

        newItem['isDir'] = False
        newItem['sortable'] = True

        listItems.append(newItem)

    # Navigation item
    elif u(jsonSection['typeId']) == "go-item-navigation":

        if 'pageId' in infoDict:
            if filtres['content']['url'] == infoDict['pageId']:
                log("content.AddItemToList: Current page item, skipping")
                return listItems

        if u(infoDict['title']) == "":
            log("content.AddItemToList: No title item, skipping")
            return listItems

        newItem = {   'genreId': 1,
                      'filtres' : GetCopy(filtres)
                  }

        newItem['title'] = urllib2.unquote(u(infoDict['title']))

        if 'image-background' in infoDict:
            newItem['image'] = infoDict['image-background']
        else:
            newItem['image'] = xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'

        newItem['fanart'] = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'

        if 'pageId' in infoDict:
            newItem['url'] = infoDict['pageId']
        elif 'entry' in infoDict:
            newItem['url'] = infoDict['entry']
        else:
            log("content.AddItemToList: Missing URL item, skipping")
            return listItems

        if 'description' in infoDict:
            newItem['plot'] = u(infoDict['description'])
        elif 'shortDescription' in infoDict:
            newItem['plot'] = u(infoDict['shortDescription'])
        else:
            newItem['plot'] = "."

        newItem['filtres']['content']['url'] =  newItem['url']

        newItem['isDir'] = True
        newItem['sortable'] = True

        newItem['filtres']['content']['genreId'] = newItem['genreId']

        listItems.append(newItem)

    else:
        log("content.AddItemToList: Unknown item type!")

    return listItems

def LoadMainMenu(filtres):
    log("content.LoadMainMenu")

    strURL = BASE_URL + "/configurations?uuid=5a0f10e5f31d1a2&gid=&appId=5955fc5423eec60006c951ef&locale=en"
    log("Accessing: " + strURL)
    jsonConfig = json.loads(cache.get_cached_content(strURL, False), encoding='utf-8')
    log("Returned:")
    log(jsonConfig)

    # ID of the start page
    strStartPage = jsonConfig['startPage']
    log("startPage: " + strStartPage)

    strPolicyKey = jsonConfig['policyKey']
    xbmcaddon.Addon().setSetting('policyKey', strPolicyKey)
    log("policyKey: " + strPolicyKey)

    jsonMenuItems = jsonConfig['menu']['menuItems']

    i=1
    liste = []

    for carte in jsonMenuItems :
        if 'pageId' in carte:
            log(u(carte['title']) + ":")
            log(carte)

            newItem = {   'genreId': i,
                          'title': urllib2.unquote(u(carte['title'])),
                          'plot': ".",
                          'image' : xbmcaddon.Addon().getAddonInfo('path')+'/icon.png',
                          'url' : u(carte['pageId']),
                          'filtres' : GetCopy(filtres)
                      }

            newItem['filtres']['content']['url'] = carte['pageId']
            newItem['isDir'] = True
            newItem['sortable'] = True
            newItem['fanart'] = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'
            newItem['filtres']['content']['genreId'] = newItem['genreId']

            # Check the different page aliases for the sections.
            if u(carte['pageAlias']) == "rattrapage" or \
               u(carte['pageAlias']) == "touslescontenus" or \
               u(carte['pageAlias']) == "direct" or \
               u(carte['pageAlias']) == "thematiques":
                liste.append(newItem)
            # Usefull for debugging, useless otherwise
            #else :
            #    newItem['title'] = newItem['title'] + " - NON FUNCTIONNAL"
            #    liste.append(newItem)

    log("content.LoadMainMenuExit")
    return liste   
    
def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
