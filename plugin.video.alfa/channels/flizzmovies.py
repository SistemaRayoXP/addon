# -*- coding: utf-8 -*-
# -*- 2025 (C) Alfa Development Group -*-
import requests
import re

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import urlparse
from core.item import Item
from platformcode import logger

from bs4 import BeautifulSoup

host = "https://flizzmovies.org"


def mainlist(item):
    logger.info()

    itemlist = list()
    itemlist.append(
        Item(
            channel=item.channel,
            action="novedades_episodios",
            title="Últimos episodios",
            url=host,
            thumbnail="https://i.imgur.com/w941jbR.png",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="novedades_anime",
            title="Últimos animes",
            url=host,
            thumbnail="https://i.imgur.com/hMu5RR7.png",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="listado",
            title="Animes",
            url=host + "browse?order=title",
            thumbnail="https://i.imgur.com/50lMcjW.png",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="search_section",
            title="-  Género",
            url=host + "browse",
            thumbnail="https://i.imgur.com/Xj49Wa7.png",
            extra="genre",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="search_section",
            title="-  Tipo",
            url=host + "browse",
            thumbnail="https://i.imgur.com/0O5U8Y0.png",
            extra="type",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="search_section",
            title="-  Año",
            url=host + "browse",
            thumbnail="https://i.imgur.com/XzPIQBj.png",
            extra="year",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="search_section",
            title="-  Estado",
            url=host + "browse",
            thumbnail="https://i.imgur.com/7LKKjSN.png",
            extra="status",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="search",
            title="Buscar...",
            thumbnail="https://i.imgur.com/4jH5gpT.png",
        )
    )

    itemlist.append(
        Item(
            channel=item.channel,
            action="setting_channel",
            title="Configurar canal",
            thumbnail=get_thumb("setting_0.png"),
        )
    )

    return itemlist


def list_all(item):
    itemlist = []
    soup = httptools.downloadpage(host, soup=True).soup.find(
        "ul", class_="container_cards"
    )
    matches = soup.find_all("li", class_="item")

    for elem in matches:
        title = elem.a.find("div", class_="card_title").text.strip()
        url = elem.a.get("href")
        thumb = elem.a.find("div", class_="card_image").img.get("data-src")
        year = re.search("\d{4}", elem.a.find("div", class_="card_info").text.strip())[
            0
        ]

        itemlist.append(
            Item(
                contentType="movie",
                title=title,
                url=url,
                thumbnail=thumb,
                infoLabels={"year": year},
            )
        )


def submenu(item):
    items = []
    soup = httptools.downloadpage(host, soup=True).soup
    containers = soup.findAll(class_="cnt")

    if item.submenu == "genres":
        containers

    elif item.submenu == "years":
        pass

    return items


def newest(categoria):
    logger.info()

    itemlist = []
    item = Item()

    try:
        if categoria in ["peliculas", "latino"]:
            item.url = host
        elif categoria == "infantiles":
            item.url = host + "/category/animacion/"
        elif categoria == "terror":
            item.url = host + "/category/torror/"
        itemlist = list_all(item)
        if "Pagina" in itemlist[-1].title:
            itemlist.pop()
    except Exception:
        import sys

        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist


def findvideos(url):
    url = "https://flizzmovies.org/pelicula/sing_2_2021"
    options = (
        BeautifulSoup(requests.get(url).content, "html5lib")
        .find("div", class_="options")
        .find_all("li", id=True)
    )

    for opt in options:
        idF = opt.get("id")
        post = {"ajax": "1", "idF": idF}
        json_data = requests.post(url, data=post).json()
        print(json_data)


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    # https://allcalidad.re/api/rest/search?post_type=movies%2Ctvshows%2Canimes&query=star&posts_per_page=16&page=1
    item.url = (
        host
        + "api/rest/search?post_type=movies%2Ctvshows%2Canimes&query="
        + texto
        + "&posts_per_page=16&page="
    )  # %texto #+ "/?page="
    item.pagina = 1
    item.extra = "busca"
    if texto != "":
        return list_all(item)
    else:
        return []
