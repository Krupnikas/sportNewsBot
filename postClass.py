from emoji import emojize
from lxml import etree
from lxml import html
from html import unescape
import requests
import logging

ChampionatUrlIdentifier = 'championat.com'
PikabuUrlIdentifier = 'pikabu.ru'

ChampionatTitlePath = "/html/body/div[5]/div[5]/div[1]/article/header/h1"
ChampionatSubtitlePath = "/html/body/div[5]/div[5]/div[1]/article/header/div[3]"
ChampionatArticlePath = "/html/body/div[5]/div[5]/div[1]/article/div"

TempGifFile = "temp.gif"

class Post:
    def __init__(self, title, text="", picture_file='', gif_url=''):
        self.title = emojize(title, use_aliases=True)
        self.text = emojize(text, use_aliases=True)
        self.pictureFile = picture_file
        self.gif_url = gif_url

    @classmethod
    def from_url(cls, url):

        if ChampionatUrlIdentifier in url:
            return cls.from_championat_url(url)
        elif PikabuUrlIdentifier in url:
            return cls.from_pikabu_url(url)
        else:
            logging.warning("Post: from_url: no identifiers found")
            return None

    @classmethod
    def from_championat_url(cls, url):

        try:
            response = requests.get(url=url)
        except Exception as ex:
            logging.warning("Post: from_url: exception: " + str(ex))
            return None

        if response.status_code != 200:
            logging.warning("Post: from_url: wrong responce code: " + str(response.status_code))
            return None

        root = html.fromstring(response.content)
        tree = etree.ElementTree(root)

        print(tree.xpath(ChampionatTitlePath))

        title = tree.xpath(ChampionatTitlePath)[0].text
        subtitle = tree.xpath(ChampionatSubtitlePath)[0].text
        text = ("".join(tree.xpath(ChampionatArticlePath)[0].itertext()))

        import re
        text = re.sub(' +', ' ', text)
        text = re.sub('\t+', '', text)
        text = re.sub('\n ', '\n', text)
        text = re.sub('\n+', '\n    ', text)
        # text = "   " + re.sub('\n \n +', '\n ', text)
        # text = re.sub('\n +', '\n    ', text)

        # for element in root.iter():
        #     try:
        #         if 'На курс нужно регистрироваться?' in element.text:
        #             print(element.text)
        #             print(tree.getpath(element))
        #     except Exception as ex:
        #         logging.debug("Post: from_url: exception: " + str(ex))
        #
        # for element in root.iter():
        #     try:
        #         if '/html/body/div[5]/div[5]/div[1]/article/' in tree.getpath(element):
        #             print("Text: " + " ".join(element.itertext()))
        #             print("Path: " + tree.getpath(element) + "\n\n")
        #             if len(text) == 0:
        #                 text = " ".join(element.itertext())
        #             elif not " ".join(element.itertext()).isspace():
        #                 text = text + "\n\n" + " ".join(element.itertext()).strip()
        #             # print(tree.getpath(element))
        #     except Exception as ex:
        #         logging.warning("Post: from_url: exception: " + str(ex))

        # print(tree.xpath("/html/body/div[5]/div[5]/div[1]/article/header/h1")[0].text)
        # print(type(tree.xpath("/html/body/div[5]/div[5]/div[1]/article/header/h1")[0]))
        #
        # print(responce.text)

        # list = [tree.iter()]
        print("Titile: " + title)
        print("Subtitle: " + subtitle)
        print("Text: " + text)

        return Post(title, text)

    @classmethod
    def from_pikabu_url(cls, url):

        try:
            response = requests.get(url=url)
        except Exception as ex:
            logging.warning("Post: from_url: exception: " + str(ex))
            return None

        if response.status_code != 200:
            logging.warning("Post: from_url: wrong responce code: " + str(response.status_code))
            return None

        raw_html  = response.content.decode("cp1251")

        import re
        match = re.search('<title>(.*?)</title>', raw_html)
        title = unescape(match.group(1) if match else '')

        if "pikabu" in title.lower():
            logging.warning("Lol, pikabu post detected and dropped")
            return None

        match = re.search('data-source="(.*.gif?)"', raw_html)
        gif_url = match.group(1) if match else ''

        if len(gif_url) == 0:
            logging.warning("Empty gif url")
            return None

        gif_url = gif_url.split(" ")[0]

        logging.info("Title: \t" + title)
        logging.info("Gif url: \t" + gif_url)

        if not gif_url:
            return None

        return Post(title=title, gif_url=gif_url)
