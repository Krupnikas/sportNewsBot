import telegram
from time import sleep

from postClass import *

# from tendo import singleton
# me = singleton.SingleInstance()

PostOnStartUp = True
NewsCheckPeriod = 60    # seconds

TOKEN = '582293326:AAG-1JSt4WHDXE9kMu4KFs7pghcIWKFdFE0'

FootballChannelId = -1001392228565
GifChannelId = -1001327157181
ChannelId = GifChannelId

BoldPrefix = '<b>'
BoldPostfix = '</b>'

ChampionatMainUrl = "https://www.championat.com/football/_worldcup.html"
TestUrl = "https://www.championat.com/football/article-3374347-fifa-prodaet-bilety-na-chempionat-mira-po-futbolu-v-rossii-v-2018-godu.html"#"https://www.championat.com/football/article-3375221-chm-2018-kakie-anglijskie-futbolnye-terminy-nado-znat-bolelschiku.html"#'https://www.championat.com/football/article-3374095-denis-cheryshev-vpervye-vyzvan-stanislavom-cherchesovym-v-sbornuju-rossii.html'

bot = telegram.Bot(token=TOKEN)
logging.basicConfig(level=logging.INFO)

def post_text(post):

    if not isinstance(post, Post):
        logging.WARNING("pos_text: post is None")
        return False
    message = BoldPrefix
    message += post.title
    message += BoldPostfix + '\n\n'
    message += post.text

    try:
        bot.send_message(ChannelId, text=message, parse_mode='HTML')
    except Exception as ex:
        logging.warning('post_text: exception: ' + str(ex))


def post_picture(picture_file, caption=''):
    try:
        bot.sendPhoto(ChannelId, photo=open(picture_file, 'rb'), caption=caption)
    except Exception as ex:
        logging.warning('post_picture: failed to send photo: ' + str(ex))

def post_gif(post):
    try:
        logging.info("Started gif upload for post " + post.title + "...")
        bot.send_video(ChannelId, video=open(post.gifFile, 'rb'), caption=post.title, timeout=60)
        logging.info("Gif successfully uploaded for post " + post.title)
    except Exception as ex:
        logging.warning('post_picture: failed to send gif: ' + str(ex))



def get_new_post():
    return ''


def get_list_of_championat_urls():
    try:
        response = requests.get(url=ChampionatMainUrl)
    except Exception as ex:
        logging.warning("get_list_of_championat_urls: exception: " + str(ex))
        return None

    if response.status_code != 200:
        logging.warning("get_list_of_championat_urls: wrong responce code: " + str(response.status_code))
        return None

    root = html.fromstring(response.content)
    links = root.cssselect('a')

    articles = []

    for link in links:
        str_link = str(link.get('href'))
        if 'article-' in str_link and str_link not in articles:
            articles.append(str_link)

    logging.info("Articles:")
    logging.info("\n".join(articles))

    return articles


def main():

    if PostOnStartUp:
        latest_post_article = ""
    else:
        latest_post_article = get_list_of_championat_urls()[0]


    while True:
        try:
            # post_text(Post(title="Hello!", text="world!"))
            p = Post.from_url("https://pikabu.ru/story/nemnozhko_tekhnoporno_vam_v_lentu_kak_quotbreyutquot_metall_6195180")
            post_gif(p)
            exit(0)
            # list = get_list_of_championat_urls()
            # latest_championat_article_url = list[0]
            # if latest_championat_article_url != latest_post_article:
            #     latest_post_article = latest_championat_article_url
            #     p = Post.from_url(latest_post_article)
            #     post_text(p)
        except Exception as ex:
            print('main: exception: ' + str(ex))
        sleep(NewsCheckPeriod)


if __name__ == '__main__':
    main()
