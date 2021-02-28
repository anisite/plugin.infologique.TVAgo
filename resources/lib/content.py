# -*- coding: utf-8 -*-
# encoding=utf8

import sys, re, xbmcaddon, xbmc, datetime, time, copy
from . import cache, html
import simplejson as json

if sys.version_info.major >= 3:
    # Python 3 stuff
    from urllib.parse import unquote, quote_plus, unquote_plus, urljoin, urlparse
    from urllib.request import Request, urlopen
else:
    # Python 2 stuff
    from urlparse import urljoin, urlparse
    from urllib import quote_plus, unquote_plus, unquote
    from urllib2 import Request, urlopen

BASE_URL_SLUG = 'https://www.qub.ca/proxy/pfu/content-delivery-service/v1/entities?slug='
#MEDIA_BUNDLE_URL = BASE_URL + 'MediaBundle/'

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

    strURL = BASE_URL_SLUG + filtres['content']['url']
    log("Accessing: " + strURL)
    jsonData = json.loads(html.get_url_txt(strURL), encoding='utf-8')
    log("Returned:")
    log(jsonData)

    jsonContainers = jsonData['associatedEntities']

    #if 'containerId' in filtres['content']:
    #    log('Current container ID:')
    #    log(filtres['content']['containerId'])

    listContainers = []
    for jsonContainer in jsonContainers :
        if 'name' in jsonContainer:
            if 'tout-voir' in jsonContainer['slug']:

            # Array of container attributes
            #aContAttributes = {}
            #log(jsonContainer['attributes'])
            #for s in jsonContainer['attributes']:
            #    aContAttributes[s['key']] = s['value']
    #
            ## Get container title
            #strContainerTitle = ""
            #if 'title' in aContAttributes:
            #    strContainerTitle = unquote(aContAttributes['title'])
    #
            #listItems = []
    #
            ## List the items in the container
            #if 'itemId' in jsonContainer:
            #    jsonItemsInContainer = jsonContainer['itemId']
    #
            #    listItems = []
            #    for jsonItem in jsonItems:
            #        if jsonItem['id'] in jsonItemsInContainer:
            #            aItemAttributes = {}
            #            for s in jsonItem['attributes']:
            #                aItemAttributes[s['key']] = s['value']
    #
            #            listItems = listItems + AddItemToList(jsonItem, aItemAttributes, filtres)
    #
    #
            ## No inner items, skip container
            #if len(listItems) == 0:
            #    continue
    #
            ## Container has no title, add inner items
            #elif strContainerTitle == "":
            #    listContainers = listContainers + listItems
    #
            ## Container title is a single character, add inner items.
            ## This is to directly show alphabetically contained items.
            #elif len(strContainerTitle) == 1:
            #    listContainers = listContainers + listItems
    #
            ## Only one container, add inner items
            #elif len(jsonContainers) == 1:
            #    listContainers = listContainers + listItems
    #
            ## Show the container
            #else:
                if 'associatedEntities' in jsonContainer:
                    for emission in jsonContainer['associatedEntities'] :
                        insert = True

                        if emission['discriminator'] == 'ExternalLinkPresentationEntity' \
                             or emission['discriminator'] == 'VideoPresentationEntity':
                            continue

                        for op in listContainers:
                            if op['containerId'] == emission['slug']:
                                insert = False
                                break
                        
                        if insert:
                            newContainer = {'genreId': 1,
                                            'title': emission['label'],
                                            'filtres' : GetCopy(filtres)
                                        }
                            image = ""
                            if 'mainImage' in emission:
                                image = emission['mainImage']['url']

                            newContainer['image'] = image #xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
                            newContainer['fanart'] = image #xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'

                            newContainer['url'] = newContainer['filtres']['content']['url']
                            newContainer['containerId'] = emission['slug']
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

    strURL = BASE_URL_SLUG + filtres['content']['containerId']
    log("Accessing: " + strURL)
    jsonData = json.loads(html.get_url_txt(strURL), encoding='utf-8')
    log("Returned:")
    log(jsonData)

    listItems = []
    if jsonData['discriminator'] == 'VideoShowEntity':
    # Get the item ids for the selected container
        for season in jsonData['knownEntities']['seasons']['associatedEntities'] :
            jsonDataSaison = json.loads(html.get_url_txt(BASE_URL_SLUG + season['slug']), encoding='utf-8')

            for emission in jsonDataSaison['associatedEntities'] :
                if emission['name'] == 'Épisodes':

                    for episode in emission['associatedEntities'] :
                        newItem = { 'genreId': 1,
                                    'title': 'Saison ' + str(season['seasonNumber']) + ' - ' + episode['label'],
                                    'sourceUrl' : episode['slug'],
                                    'filtres' : GetCopy(filtres)
                                    }
                        newItem['isDir'] = False
                        newItem['sortable'] = False
                        newItem['url'] = episode['slug']
                        newItem['filtres']['content']['containerId'] = season['slug']
                        newItem['image'] = episode['mainImage']['url']
                        newItem['fanart'] = episode['mainImage']['url']
                        newItem['plot'] = episode.get('description')
                        newItem['duration'] = episode['durationMillis'] / 1000
                        newItem['startDate'] = episode['activationDate']
                        newItem['genre'] = ''
                        newItem['rating'] = ''
                
                        listItems.append(newItem)
               

    elif jsonData['discriminator'] == 'VideoSeasonEntity':
        print("null")
            #if unquote(u(jsonContainer['id'])) == filtres['content']['containerId']:
            #    jsonItemsInContainer = jsonContainer['itemId']

    #jsonItems = jsonData['item']
#
    #listItems = []
    #for jsonItem in jsonItems :
    #    if jsonItem['id'] in jsonItemsInContainer:
    #        log(jsonItem['attributes'])
    #        dict = {}
    #        for s in jsonItem['attributes']:
    #            dict[s['key']] = s['value']
#
    #        listItems = listItems + AddItemToList(jsonItem, dict, filtres)

    log("content.LoadContainerItemsExit")
    return listItems

def LoadItems(filtres):
    log("content.LoadItems")
    log(filtres)

    strURL = BASE_URL_SLUG + "/page/"+ filtres['content']['url'] +"?uuid=5a0f10e5f31d1a2&gid=&appId=5955fc5423eec60006c951ef&locale=en"
    log("Accessing: " + strURL)
    jsonData = json.loads(html.get_url_txt(strURL), encoding='utf-8')
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
                      'title': unquote(u(infoDict['title'])),
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

        newItem['title'] = unquote(u(infoDict['title']))

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

    strURL = BASE_URL_SLUG + "/qubtv-chaines"
    log("Accessing: " + strURL)
    jsonConfig = json.loads(html.get_url_txt(strURL, False), encoding='utf-8')
    log("Returned:")
    log(jsonConfig)

    # ID of the start page
    #strStartPage = jsonConfig['startPage']
    #log("startPage: " + strStartPage)

    #strPolicyKey = jsonConfig['policyKey']
    #xbmcaddon.Addon().setSetting('policyKey', strPolicyKey)
    #log("policyKey: " + strPolicyKey)

    jsonMenuItems = jsonConfig['associatedEntities']

    liste = []

    for carte in jsonMenuItems :
        #log(u(carte['title']) + ":")
        #log(carte)

        if 'mainImage' in carte:
            image = carte['mainImage']['url']

            newItem = {   'genreId': 1,
                            'title': carte['label'],
                            'plot': "Chaîne " + carte['label'],
                            'image' : image,
                            'url' : carte['slug'],
                            'filtres' : GetCopy(filtres)
                        }

            newItem['filtres']['content']['url'] = carte['slug']
            newItem['isDir'] = True
            newItem['sortable'] = False
            newItem['fanart'] = xbmcaddon.Addon().getAddonInfo('path') + '/resources/fanart.jpg'
            newItem['filtres']['content']['genreId'] = newItem['genreId']

            liste.append(newItem)

    # Add start page container
    #strStartPageUrl = jsonConfig['startPage']

    log("content.LoadMainMenuExit")
    return liste

def log(msg):
    """ function docstring """
    #if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
    xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
