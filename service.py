import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp', '') ).decode("utf-8")

sys.path.append (__resource__)

from buscador import Buscador, log, normalizeString

if xbmcvfs.exists(__temp__):
  log("inicio", "Borrando directorio")
  shutil.rmtree(__temp__)
log("inicio", "Creando directorio")
xbmcvfs.mkdirs(__temp__)

def Search():
  return ""

def Download(url):
  subtitle_list = []
  log("Download:", url)
  buscador = Buscador()
  path =  os.path.join( __temp__, "%s.%s" %(str(uuid.uuid4()), "srt"))
  log("d1", path)
  buscador.DescargarCapitulo(url, path)
  subtitle_list.append(path)
  return subtitle_list

def get_params(string=""):
  param=[]
  if string == "":
    paramstring=sys.argv[2]
  else:
    paramstring=string
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]

  return param

params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
  log( __name__, "action '%s' called" % params['action'])
  item = {}

  if xbmc.Player().isPlaying():
    item['temp']               = False
    item['rar']                = False
    item['mansearch']          = False
    item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
    item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
    item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
    item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
    item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
    item['file_original_path'] = xbmc.Player().getPlayingFile().decode('utf-8')                 # Full path of a playing file
    item['3let_language']      = [] #['scc','eng']

  else:
    item['temp'] = False
    item['rar'] = False
    item['mansearch'] = False
    item['year'] = ""
    item['season'] = ""
    item['episode'] = ""
    item['tvshow'] = ""
    item['title'] = takeTitleFromFocusedItem()
    item['file_original_path'] = ""
    item['3let_language'] = []

  PreferredSub = params.get('preferredlanguage')

  if 'searchstring' in params:
    item['mansearch'] = True
    item['mansearchstr'] = params['searchstring']

  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    if lang == "Portuguese (Brazil)":
      lan = "pob"
    elif lang == "Greek":
      lan = "ell"
    else:
      lan = xbmc.convertLanguage(lang,xbmc.ISO_639_2)

    item['3let_language'].append(lan)

  if item['title'] == "":
    log( __name__, "VideoPlayer.OriginalTitle not found")
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

  if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
    item['season'] = "0"                                                          #
    item['episode'] = item['episode'][-1:]

  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]

  log("SubtitulosJulian:", item)

  buscador = Buscador()
  infoFichero = buscador.ParsearFichero(item['title'])
  log("SubtitulosJulian:", infoFichero)
  seriesCoincidentes = buscador.ObtenerSeriesCoincidentes(infoFichero['title'])
  log("SubtitulosJulian:", seriesCoincidentes)
  for serie in seriesCoincidentes:
    enlaceSerie = serie["href"]
    trozos = enlaceSerie.split("/")
    serieID = trozos[len(trozos)-1]
    log("aaa", serieID)
    capitulo = buscador.ObtenerCapitulo(serieID, str(infoFichero['season']), '{:02d}'.format(infoFichero['episode']))
    log("bbb", capitulo)
    for version in capitulo.versiones:
      for idioma in version.idiomas:
        url = "plugin://%s/?action=download&link=%s" % (__scriptid__,idioma.enlace)
        listitem = xbmcgui.ListItem(label          = idioma.nombre,
                                    label2         = capitulo.texto + " " + version.nombre
                                    )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)

elif params['action'] == 'download':
  log( __name__, "action '%s' called" % params['action'])
  subs = Download(params["link"])
  for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))