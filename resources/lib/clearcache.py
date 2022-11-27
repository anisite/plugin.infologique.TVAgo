# -*- coding: utf-8 -*-

import os
import sys

import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

addon = Addon('plugin.infologique.TVAgo')
addon_cache_basedir = os.path.join(xbmc.translatePath(addon.getAddonInfo('path')),".cache")

if sys.argv[1].lower() == "full":
    print("["+addon.getAddonInfo('name')+"] deleting full cache")
    for root, dirs, files in os.walk(addon_cache_basedir):
        for file in files:
            xbmcvfs.delete(os.path.join(root,file))

