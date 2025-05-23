# -*- coding: utf-8 -*-
# -*- Channel CheemsPorn -*-
# -*- Created for Alfa-addon -*-
# -*- By the Alfa Develop Group -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAdultChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_A
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES_A
list_quality_tvshow = []
list_quality = list_quality_movies + list_quality_tvshow
list_servers = AlfaChannelHelper.LIST_SERVERS_A

forced_proxy_opt = 'ProxySSL'

#########           Falla visualizacion de thumbnails  380x214
                                    # solo se ven      320x180

# https://cheemsporn.com/  https://cheemsporno.com/


canonical = {
             'channel': 'cheemsporn', 
             'host': config.get_setting("current_host", 'cheemsporn', default=''), 
             'host_alt': ["https://cheemsporn.com/"], 
             'host_black_list': ["https://hdporn92.me/", "https://cheemsporno.com/"], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 5
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = ''
tv_path = ''
language = []
url_replace = []


finds = {'find': dict([('find', [{'tag': ['div', 'section'], 'id': ['primary']}]),
                       ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]),
         'categories': dict([('find', [{'tag': ['div'], 'id': ['primary']}]),
                             ('find_all', [{'tag': ['article'], 'class': re.compile(r"^post-\d+")}])]), 
         'search': {}, 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']], 
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['pagination']}]), 
                            ('find_all', [{'tag': ['a'], '@POS': [-1],
                            '@ARG': 'href', '@TEXT': '\/page\/(\d+)'}])]), 
         'plot': {}, 
         # 'findvideos': {'find_all': [{'tag': ['option'], '@ARG': 'value'}]}, 
         # 'findvideos': {'find': [{'tag': ['header'], 'class': ['entry-header']}]}, 
         'findvideos': {'find_all': [{'tag': ['header'], 'class': ['entry-header']}]}, 
         'title_clean': [['[\(|\[]\s*[\)|\]]', ''],['(?i)\s*videos*\s*', '']],
         'quality_clean': [['(?i)proper|unrated|directors|cut|repack|internal|real|extended|masted|docu|super|duper|amzn|uncensored|hulu', '']],
         'url_replace': [], 
         'profile_labels': {
                            # 'list_all_stime': dict([('find', [{'tag': ['div', 'span'], 'class': ['dur']}]),
                                                    # ('get_text', [{'strip': True}])]),
                            'list_all_quality': dict([('find', [{'tag': ['div', 'span'], 'class': ['hd-video']}]),
                                                      ('get_text', [{'strip': True}])]),
                           },
         'controls': {'url_base64': False, 'cnt_tot': 24, 'reverse': False, 'profile': 'default'}, 
         'timeout': timeout}
AlfaChannel = DictionaryAdultChannel(host, movie_path=movie_path, tv_path=tv_path, movie_action='play', canonical=canonical, finds=finds, 
                                     idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                     list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                     channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos", action="list_all", url=host + "page/1?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Más visto", action="list_all", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado", action="list_all", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas largo", action="list_all", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Pornstars", action="section", url=host + "actors/page/1", extra="PornStar"))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="section", url=host + "categories", extra="Categorias"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def section(item):
    logger.info()
    
    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()
    
    findS = finds.copy()
    findS['controls']['action'] = 'findvideos'
    
    return AlfaChannel.list_all(item, finds=findS, **kwargs)
    # return AlfaChannel.list_all(item, **kwargs)


def findvideos(item):
    logger.info()
    
    # return AlfaChannel.get_video_options(item, item.url, data='', matches_post=None, 
                                         # verify_links=False, findvideos_proc=True, **kwargs)
    return AlfaChannel.get_video_options(item, item.url, matches_post=findvideos_matches, 
                                         verify_links=False, generictools=True, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()
    matches = []
    
    findS = AHkwargs.get('finds', finds)
    
    soup = AHkwargs.get('soup', {})
    
    header = soup.find('header', class_='entry-header')
    
    casa = soup.find_all('option')
    descargas = soup.find_all('a', class_='download-link')
    casa = casa + descargas
    if soup.find('source', type='video/mp4'):
        casa.append(soup.find('source', type='video/mp4')) 
    if soup.find('iframe'):
        casa.append(soup.find('iframe')) 
    copias=[]
    for elem in casa:
        elem_json = {}
        #logger.error(elem)
        
        try:
            url = elem.get('href', '') or elem.get('src', '') or elem.get('value', '')
            if "eporner.com/dload/" in url:
                id = scrapertools.find_single_match(url, '/dload/([A-z0-9]+)/')
                url = "https://www.eporner.com/embed/%s" %id
            if "send.now" in url: continue
            
            #quitar repetidos
            marca =url
            if marca.endswith("/"): marca=marca[:-1]
            marca = marca.replace("embed-", "").replace(".html", "").replace("\\u0026dl=1", '').strip()
            marca = marca.split("/")
            if ".mp4" in marca[-1] or ".m3u" in marca[-1]:
                marca = marca[:-1]
            marca = marca[-1]
            if not marca in copias and marca: 
                copias.append(marca)
                elem_json['url'] = url
            
            elem_json['language'] = ''

        except:
            logger.error(elem)
            logger.error(traceback.format_exc())

        if not elem_json.get('url', ''): continue

        matches.append(elem_json.copy())

    return matches, langs


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)
    
    item.url = "%s?s=%s&filter=latest" % (host, texto.replace(" ", "+"))
    
    try:
        if texto:
            item.c_type = "search"
            item.texto = texto
            return list_all(item)
        else:
            return []
    
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []
