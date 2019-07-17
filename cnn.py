import newspaper
import requests
from googletrans import Translator

url = 'https://www.wired.com/story/robots-alone-cant-solve-amazons-labor-woes/'
article = newspaper.Article(url)
article.download()
article.parse()
article.nlp()

translator = Translator()
title = translator.translate(article.title, dest='ru').text
body = translator.translate(article.text, dest='ru').text

print(title)
print(body)
