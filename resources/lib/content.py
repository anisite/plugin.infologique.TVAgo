# -*- coding: utf-8 -*-
# encoding=utf8

import urllib2, cache, re, xbmcaddon, html, xbmc, datetime, time, copy
import simplejson as json

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

def LoadContainers(filtres):
    log("content.LoadContainers")
    log(filtres)

    strURL = BASE_URL + "/page/"+ filtres['content']['url'] +"?uuid=5a0f10e5f31d1a2&gid=&appId=5955fc5423eec60006c951ef&locale=en"
    log("Accessing: " + strURL)
    jsonData = json.loads(cache.get_cached_content(strURL), encoding='utf-8')
    log("Returned:")
    log(jsonData)

    jsonItems = jsonData['item']
    jsonContainers = jsonData['container']

    if 'containerId' in filtres['content']:
        log('Current container ID:')
        log(filtres['content']['containerId'])

    listContainers = []
    for jsonContainer in jsonContainers :

        # Array of container attributes
        aContAttributes = {}
        log(jsonContainer['attributes'])
        for s in jsonContainer['attributes']:
            aContAttributes[s['key']] = s['value']

        # Get container title
        strContainerTitle = ""
        if 'title' in aContAttributes:
            strContainerTitle = urllib2.unquote(u(aContAttributes['title']))

        listItems = []

        # List the items in the container
        if 'itemId' in jsonContainer:
            jsonItemsInContainer = jsonContainer['itemId']

            listItems = []
            for jsonItem in jsonItems:
                if jsonItem['id'] in jsonItemsInContainer:
                    aItemAttributes = {}
                    for s in jsonItem['attributes']:
                        aItemAttributes[s['key']] = s['value']

                    listItems = listItems + AddItemToList(jsonItem, aItemAttributes, filtres)


        # No inner items, skip container
        if len(listItems) == 0:
            continue

        # Container has no title, add inner items
        elif strContainerTitle == "":
            listContainers = listContainers + listItems

        # Container title is a single character, add inner items.
        # This is to directly show alphabetically contained items.
        elif len(strContainerTitle) == 1:
            listContainers = listContainers + listItems

        # Only one container, add inner items
        elif len(jsonContainers) == 1:
            listContainers = listContainers + listItems

        # Show the container
        else:
            newContainer = {   'genreId': 1,
                               'title': strContainerTitle,
                               'filtres' : GetCopy(filtres)
                           }

            newContainer['image'] = xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
            newContainer['fanart'] = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'

            newContainer['url'] = newContainer['filtres']['content']['url']
            newContainer['containerId'] = urllib2.unquote(u(jsonContainer['id']))
            newContainer['plot'] = "."

            newContainer['filtres']['content']['containerId'] =  newContainer['containerId']
            newContainer['filtres']['content']['genreId'] = newContainer['genreId']

            newContainer['isDir'] = True
            newContainer['sortable'] = True

            listContainers.append(newContainer)

    log("content.LoadContainersExit")
    return listContainers

def LoadContainerItems(filtres):
    log("content.LoadContainerItems")
    log(filtres)

    strURL = BASE_URL + "/page/"+ filtres['content']['url'] +"?uuid=5a0f10e5f31d1a2&gid=&appId=5955fc5423eec60006c951ef&locale=en"
    log("Accessing: " + strURL)
    jsonData = json.loads(cache.get_cached_content(strURL), encoding='utf-8')
    log("Returned:")
    log(jsonData)

    jsonContainers = jsonData['container']

    # Get the item ids for the selected container
    for jsonContainer in jsonContainers :
        if urllib2.unquote(u(jsonContainer['id'])) == filtres['content']['containerId']:
            jsonItemsInContainer = jsonContainer['itemId']

    jsonItems = jsonData['item']

    listItems = []
    for jsonItem in jsonItems :
        if jsonItem['id'] in jsonItemsInContainer:
            log(jsonItem['attributes'])
            dict = {}
            for s in jsonItem['attributes']:
                dict[s['key']] = s['value']

            listItems = listItems + AddItemToList(jsonItem, dict, filtres)

    log("content.LoadContainerItemsExit")
    return listItems

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

        # not a container remove the id
        if 'containerId' in newItem['filtres']['content']:
            del newItem['filtres']['content']['containerId']

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

        # not a container remove the id
        if 'containerId' in newItem['filtres']['content']:
            del newItem['filtres']['content']['containerId']

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

    liste = []

    for carte in jsonMenuItems :
        if 'pageId' in carte:
            log(u(carte['title']) + ":")
            log(carte)

            newItem = {   'genreId': 1,
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

    # Add start page container
    strStartPageUrl = jsonConfig['startPage']

    newContainer = {   'genreId': 1,
                       'title': "Acceuil",
                       'filtres' : GetCopy(filtres)
                   }

    newContainer['image'] = xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
    newContainer['fanart'] = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'

    newContainer['url'] = strStartPageUrl
    newContainer['plot'] = "Éléments disponibles sur la page d'acceuil"

    newContainer['filtres']['content']['url'] =  newContainer['url']
    newContainer['filtres']['content']['genreId'] = newContainer['genreId']

    newContainer['isDir'] = True
    newContainer['sortable'] = True

    liste.append(newContainer)

    log("content.LoadMainMenuExit")
    return liste

def log(msg):
    """ function docstring """
    if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
        xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
