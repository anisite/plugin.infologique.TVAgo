# -*- coding: utf-8 -*-

import copy
import content
#from operator import itemgetter

def get_liste_emissions(filtres):
    liste = content.get_liste(filtres['content']['genreId'])
    return content.formatListe(liste, filtres)

def ListeVideosFiltrees(mediaBundleId, filtres):
    liste = content.getListeOfVideo(mediaBundleId, filtres)
    filtresShow = filtres['show']
    if len(filtresShow) == 0:
        return liste
    for key in filtresShow:
        if filtresShow[key] != '':
            liste = filterBy(key, filtresShow[key], liste)

    return liste

def ListeVideosGroupees(filtres):
    filtresShow = filtres['show']
    liste = ListeVideosFiltrees(filtres['content']['mediaBundleId'], filtres)
    index = 0
    for value in filtresShow.values():
        if value != '':
            index = index + 1
        else:
            break

    if index >= len(filtresShow):
        return liste
    else:
        groupBy = filtresShow.keys()[index]
        showsGroupes = {}
        cle = ''
        
        for show in liste:
            cle = show[groupBy]
            if cle in showsGroupes:
                showsGroupes[cle].append(show)
            else:
                showsGroupes[cle] = [show]

        if len(showsGroupes) == 1: #S'il n'y a qu'un seul répertoire, l'ouvrir immédiatement
            newfiltre = getCopy(filtres)
            newfiltre['show'][groupBy] = cle
            return ListeVideosGroupees(newfiltre)

        newDirs = []
        
        for key in showsGroupes:
            theShows = showsGroupes[key]
            
            #------ESSAYER DE TROUVER L'EPISODE COMPLET
            j=0
            for show in theShows :
                if content.isIntegral(show):
                    break
                else:
                    j=j+1
            if j>=len(theShows):
                j=0

            theShows =popEpisodeComplet(theShows) #Amener l'episode complet en haut de liste
            oneShow = theShows[0]

            #----------------------
               
            if len(theShows) == 1: #Si un seul show est contenu dans un répertoire, l'ouvrir immédiatement
                oneShow['isDir'] = False
                if type(key) == int:
                    oneShow['nom'] = str(key) + ' - ' + oneShow['nom']
                else:
                    oneShow['nom'] = key + ' - ' + oneShow['nom']
            else:
                oneShow['isDir'] = True
                if type(key) == int:
                    oneShow['nom'] = str(key)
                else:
                    oneShow['nom'] = key

            oneShow['filtres'] = getCopy(filtres)
            oneShow['filtres']['show'][groupBy] = oneShow[groupBy]
            oneShow['filtres']['sourceId'] = oneShow['sourceId']
            newDirs.append(oneShow)

        
        #newDirs = sorted(newDirs, key=itemgetter('startDate'), reverse=True)
        return popEpisodeComplet(newDirs) #Amener l'episode complet en haut de liste

def popEpisodeComplet(liste):
    j=0
    for item in liste :
        if content.isIntegral(item):
            break
        else:
            j=j+1

    if j>=len(liste):
        j=0
    if len(liste)>0: 
        liste.insert(0,liste.pop(j))
    return liste




def getCopy(item):
    return copy.deepcopy(item)

def filterBy(key, value, liste):
    newList = []
    for item in liste:
        if item[key] == value:
            newList.append(item)

    return newList
