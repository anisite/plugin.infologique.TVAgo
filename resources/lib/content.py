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

BASE_URL_SLUG = 'https://api.qub.ca/content-delivery-service/v1/entities?slug='

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

    listContainers = []
    if 'knownEntities' in jsonData and 'videoStream' in jsonData['knownEntities']:
        enDirect = jsonData['knownEntities']['videoStream']
        newContainer = {'genreId': 1,
                        'title': '-- En direct --',
                        'filtres' : GetCopy(filtres)
                        }
        #image = ""
        #if 'mainImage' in emission:
        image = enDirect['image']['url']

        newContainer['image'] = image #xbmcaddon.Addon().getAddonInfo('path')+'/icon.png'
        newContainer['fanart'] = xbmcaddon.Addon().getAddonInfo('path')+'/fanart.jpg'

        newContainer['url'] = u'ref:' + enDirect['slug']
        newContainer['containerId'] = enDirect['slug']
        newContainer['plot'] = "."

        newContainer['filtres']['content']['containerId'] =  newContainer['containerId']
        newContainer['filtres']['content']['genreId'] = newContainer['genreId']

        newContainer['isDir'] = True
        newContainer['isForceDir'] = False
        newContainer['duration'] = 0
        #newContainer['sourceUrl'] = newContainer['url']
        newContainer['startDate'] = ''
        newContainer['genre'] = ''
        newContainer['rating'] = 'Everyone'
        newContainer['sortable'] = True 

        listContainers.append(newContainer)

    for jsonContainer in jsonContainers :
        if 'name' in jsonContainer:
            if 'tout-voir' in jsonContainer['slug']:

            ## Show the container
            #else:
                if 'associatedEntities' in jsonContainer:
                    for emission in jsonContainer['associatedEntities'] :
                        insert = True

                        # inclue seulement les émissions
                        if emission['discriminator'] == 'VideoShowPresentationEntity' or emission['discriminator'] == 'VideoShowEntity':

                            for op in listContainers:
                                if "slug" not in emission or ("slug" in emission and op['containerId'] == emission['slug']):
                                    insert = False
                                    break

                            if insert:
                                newContainer = {'genreId': 1,
                                                'title': emission['label'],
                                                'filtres' : GetCopy(filtres)
                                            }
                                image = ""
                                if 'mainImage' in emission:
                                    if 'crops' in emission['mainImage'] and '1' in emission['mainImage']['crops'] and 'url' in emission['mainImage']['crops'][1]:
                                        image = emission['mainImage']['crops'][1]['url']
                                    else:
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
    try:
    
        if jsonData['discriminator'] == 'VideoShowEntity':

            # emission avec des saisons
            if 'seasons' in jsonData['knownEntities']:
                for season in jsonData['knownEntities']['seasons']['associatedEntities']:
                    strURL = BASE_URL_SLUG + season['slug']
                    log("Accessing: " + strURL)

                    jsonDataSaison = json.loads(html.get_url_txt(strURL), encoding='utf-8')

                    for emission in jsonDataSaison['knownEntities']['relatedVideos']['associatedEntities'] :
                        #if emission['name'] == 'Épisodes':

                            for episode in emission['associatedEntities'] :
                                newItem = { 'genreId': 1,
                                            'title': 'Saison ' + str(season['seasonNumber']) + ' - ' + emission['name'] + ' - ' + episode['label'],
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

            # emission principal sans saison
            if 'mainVideo' in jsonData['knownEntities']:
                episode = jsonData['knownEntities']['mainVideo']

                #for episode in emission['associatedEntities'] :
                newItem = { 'genreId': 1,
                            'title':  episode['label'],
                            'sourceUrl' : episode['slug'],
                            'filtres' : GetCopy(filtres)
                            }
                newItem['isDir'] = False
                newItem['sortable'] = False
                newItem['url'] = episode['slug']
                newItem['filtres']['content']['containerId'] = episode['slug']
                newItem['image'] = episode['mainImage']['url']
                newItem['fanart'] = episode['mainImage']['url']
                newItem['plot'] = episode.get('description')
                newItem['duration'] = episode['durationMillis'] / 1000
                newItem['startDate'] = episode['activationDate']
                newItem['genre'] = ''
                newItem['rating'] = ''

                listItems.append(newItem)
 
            # emission sans saison. Contenu additionel.
            if 'relatedVideos' in jsonData['knownEntities']:

                for emission in jsonData['knownEntities']['relatedVideos']['associatedEntities'] :
                    #if emission['name'] == 'Épisodes':

                        for episode in emission['associatedEntities'] :
                            newItem = { 'genreId': 1,
                                        'title': emission['name'] + ' - ' + episode['label'],
                                        'sourceUrl' : episode['slug'],
                                        'filtres' : GetCopy(filtres)
                                        }
                            newItem['isDir'] = False
                            newItem['sortable'] = False
                            newItem['url'] = episode['slug']
                            newItem['filtres']['content']['containerId'] = emission['slug']
                            newItem['image'] = episode['mainImage']['url']
                            newItem['fanart'] = episode['mainImage']['url']
                            newItem['plot'] = episode.get('description')
                            newItem['duration'] = episode['durationMillis'] / 1000
                            newItem['startDate'] = episode['activationDate']
                            newItem['genre'] = ''
                            newItem['rating'] = ''

                            listItems.append(newItem)
    except:
        log("content.LoadContainerItemsExit: Error occured while processing")

    log("content.LoadContainerItemsExit")
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
    #5813221784001/sd748Ih4e_default
    xbmcaddon.Addon().setSetting('policyKey', html.get_policykey('5813221784001', 'sd748Ih4e', 'default'))
    #log("policyKey: " + strPolicyKey)

    jsonMenuItems = jsonConfig['associatedEntities']

    liste = []

    liste = LoadDirect(filtres)

    for carte in jsonMenuItems :
        #log(u(carte['title']) + ":")
        #log(carte)

        if 'mainImage' in carte:
            image = carte['mainImage']['url']

            newItem = {   'genreId': 1,
                            'title': carte['label'],
                            'plot': u'Chaîne ' + carte['label'],
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

def LoadDirect(filtres):
    log("content.LoadDirect")

    try:
        strURL = BASE_URL_SLUG + "/accueil/qubtv-en-direct"
        log("Accessing: " + strURL)
        jsonPostesConfig = json.loads(html.get_url_txt(strURL, False), encoding='utf-8')
        log("Returned:")
        log(jsonPostesConfig)

        jsonListPostes = jsonPostesConfig['associatedEntities']

        liste = []

        for postesLvl1 in jsonListPostes :
            for posteLvl2 in postesLvl1['associatedEntities'] :

                strURL = BASE_URL_SLUG + posteLvl2['slug']
                log("Accessing: " + strURL)
                jsonPosteDetail = json.loads(html.get_url_txt(strURL, False), encoding='utf-8')
                log("Returned:")
                log(jsonPosteDetail)

                if jsonPosteDetail['discriminator'] == 'VideoStreamEntity':
                    newItem = { 'genreId': 1,
                                'title': "En Direct " + jsonPosteDetail['sourceReference']['name'],
                                'sourceUrl' : u'ref:' + jsonPosteDetail['referenceId'],
                                'url' : u'ref:' + jsonPosteDetail['referenceId'],
                                'filtres' : GetCopy(filtres),
                                'isDir' : False,
                                'sortable' : False,
                                'image' : jsonPosteDetail['image']['url'],
                                'fanart' : jsonPosteDetail['image']['url'],
                                'plot' : '',
                                'duration' : '',
                                'startDate' : '',
                                'genre' : '',
                                'rating' : ''
                                }
                    newItem['filtres']['content']['containerId'] = newItem['sourceUrl']
                    
                    liste.append(newItem)
    except:
        log("content.LoadDirect: Error occured while processing")


    log("content.LoadDirectExit")
    return liste


def log(msg):
    """ function docstring """
    #if xbmcaddon.Addon().getSetting('DebugMode') == 'true':
    xbmc.log('[%s - DEBUG]: %s' % (xbmcaddon.Addon().getAddonInfo('name'), msg))
