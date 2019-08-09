import os
from time import sleep
from datetime import datetime
import logging
import bs4
import sys
import random
import requests
import newspaper
import schedule
import time
from zen import ZenPublisher
import googletrans
import pymorphy2

login = "bot3@nightone.tech"
password = "botnightone"
editor_link = "https://zen.yandex.ru/profile/editor/id/5d49b5f7ecfb8000acf23057"

category = "business"
rootUrl = 'https://www.wired.com'
mainUrl = f"https://www.wired.com/category/{category}/"

def get_links(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, features="lxml")
    feed = soup.find("div", {"class": "cards-component"})
    cards = feed.findAll("li", {"class": "card-component__description"})
    links = []
    for card in cards:
        link = card.find("a")
        links.append(rootUrl + link['href'])
    return links


def postArticleToYandexZen(article):

    trans = googletrans.Translator()
    
    article.nlp()

    tags = [category]
    tags = tags + article.keywords

    morph = pymorphy2.MorphAnalyzer()

    keywords = []
    for tag in tags:
        tag = trans.translate(tag, dest='ru').text
        tag = morph.parse(tag)[0]
        if len(tag.normal_form) > 3 and 'NOUN' in tag.tag:
            keywords.append(tag.normal_form)

    description = trans.translate(article.summary, dest='ru').text
    description = description.split('.')[0]

    print(keywords)

    publisher = ZenPublisher()
    publisher.auth(login, password)
    publisher.createNewArticle(editor_link)
    publisher.fillArticle(article)
    publisher.publish(keywords, description)


def makePost():
    links = get_links(mainUrl)
    article = newspaper.Article(links[1])
    article.download()
    article.parse()
    postArticleToYandexZen(article)


makePost()
exit(0)

schedule.every().day.at("20:13").do(makePost)
while True:
    schedule.run_pending()
    time.sleep(5)
