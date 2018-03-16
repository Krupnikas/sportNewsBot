from emoji import emojize
from lxml import etree
from lxml import html
import requests
import logging

ChampionatUrlIdentifier = 'championat.com'
ChampionatTitlePath = "/html/body/div[5]/div[5]/div[1]/article/header/h1"

class Post:
    def __init__(self, header, text, picture_file=''):
        self.header = emojize(header, use_aliases=True)
        self.text = emojize(text, use_aliases=True)
        self.pictureFile = picture_file

    @classmethod
    def from_url(cls, url):

        if ChampionatUrlIdentifier in url:
            return cls.from_championat_url(url)
        else:
            logging.warning("Post: from_url: no identifiers found")
            return None

    @classmethod
    def from_championat_url(cls, url):

        try:
            responce = requests.get(url=url)
        except Exception as ex:
            logging.warning("Post: from_url: exception: " + str(ex))
            return None

        if responce.status_code != 200:
            logging.warning("Post: from_url: wrong responce code: " + str(responce.status_code))
            return None

        root = html.fromstring(responce.content)
        tree = etree.ElementTree(root)

        for element in root.iter():
            try:
                if 'Черчесов вспомнил ' in element.text:
                    print(element.text)
                    print(tree.getpath(element))
            except Exception as ex:
                logging.debug("Post: from_url: exception: " + str(ex))

        print(tree.xpath("/html/body/div[5]/div[5]/div[1]/article/header/h1")[0].text)
        print(type(tree.xpath("/html/body/div[5]/div[5]/div[1]/article/header/h1")[0]))

        # print(responce.text)

        # list = [tree.iter()]
        # print(list)

        # for element in tree.xpath('//text()'):
        #     if 'Черчесов вспомнил ' in element:
        #         print(element)
        #         print(element.getroottree().getpath(element))

        exit(0)
        return Post("ChampHeader", "ChampText :balloon:, Hello!")
