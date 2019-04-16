import telegram
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
from datetime import datetime
import logging
from postClass import *
import bs4

# from tendo import singleton
# me = singleton.SingleInstance()

PostOnStartUp = False
NewsCheckPeriod = 5 * 60    # seconds

ArticlePostTimeMoscowOffset = 19.00  # Hours 19:00 Moscow UTC+3
ArticlePostTimeUtcOffsetSeconds = (ArticlePostTimeMoscowOffset - 3) * 60 * 60

LastPostDay = 0

TOKEN = '582293326:AAG-1JSt4WHDXE9kMu4KFs7pghcIWKFdFE0'

postedLinksFilename = "posted.csv"
postedLinks = []

driver = None

if os.path.isfile(postedLinksFilename):
    with open(postedLinksFilename) as f:
        postedLinks = postedLinks + f.readlines()
else:
    print(f"Posted links file {postedLinksFilename} not found and will be created")

FootballChannelId = -1001392228565
GifChannelId = -1001327157181
ChannelId = GifChannelId
# ChannelId = FootballChannelId

BoldPrefix = '<b>'
BoldPostfix = '</b>'

# ChampionatMainUrl = "https://www.championat.com/football/_worldcup.html"
PikabuMainUrl = "https://pikabu.ru/search?t=Гифка%2CЖивотные&r=7&d=0&D=40000"
# TestUrl = "https://www.championat.com/football/article-3374347-fifa-prodaet-bilety-na-chempionat-mira-po-futbolu-v-rossii-v-2018-godu.html"#"https://www.championat.com/football/article-3375221-chm-2018-kakie-anglijskie-futbolnye-terminy-nado-znat-bolelschiku.html"#'https://www.championat.com/football/article-3374095-denis-cheryshev-vpervye-vyzvan-stanislavom-cherchesovym-v-sbornuju-rossii.html'

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
        bot.sendDocument(ChannelId, document=open(picture_file, 'rb'), caption=caption)
    except Exception as ex:
        logging.warning('post_picture: failed to send photo: ' + str(ex))

def post_gif(post):
    try:
        logging.info("Started gif upload for post " + post.title + "...")
        bot.send_video(ChannelId, video=post.gif_url, caption=post.title, timeout=60)
        logging.info("Gif successfully uploaded for post " + post.title)
        return True
    except Exception as ex:
        logging.warning('post_picture: failed to send gif: ' + str(ex))
        return False



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

def get_multiple_posts(url):
    print(url)
    try:
        response = requests.get(url=url)
    except Exception as ex:
        logging.warning("get_list_of_championat_urls: exception: " + str(ex))
        return []

    if response.status_code != 200:
        logging.warning("get_list_of_championat_urls: wrong responce code: " + str(response.status_code))
        return []

    soup = bs4.BeautifulSoup(response.content, features="lxml")
    feed = soup.find("div", {"class": "stories-feed__container"})
    posts = feed.findAll("article", {"class": "story"}, recursive=False)

    parsed_posts = []

    for post in posts:
        # print(post)
        player = post.find("div", {"class": "player"})
        if player is None:
            logging.warning(f"Post dropped. No player element")
            continue
        gif_url = player['data-source']
        if ".gif" not in gif_url:
            logging.warning(f"Post dropped. Not a gif url: {gif_url}")
            continue
        if gif_url in postedLinks:
            print(f"Posted already: {post_url}")
            continue
        title = post.find("h2", {"class": "story__title"}).text.strip()
        if title[0] == "-":
            title = title[1:]
        tags = [tag.text.lower() for tag in post.findAll("a", {"class": "tags__tag"})]
        parsed_posts.append(Post(title, gif_url=gif_url, tags=tags))

    return parsed_posts


def authentificate_in_yandex_zen():

    global driver

    login = "krupnik35"
    print(f"Password for {login}: ")
    password = "Klazklaz37"  # input()

    driver = webdriver.Chrome()
    driver.get(
        "https://passport.yandex.ru/auth?origin=zen&retpath=https%3A%2F%2Fzen.yandex.ru%2Fid%2F5c8ce13954593600b40ba8e4")
    login_field = driver.find_element_by_id("passp-field-login")

    login_field.send_keys(login)
    driver.find_element_by_css_selector(
        ".control.button2.button2_view_classic.button2_size_l.button2_theme_action.button2_width_max.button2_type_submit.passp-form-button").click()

    sleep(1)
    password_field = driver.find_element_by_id("passp-field-passwd")
    password_field.send_keys(password)
    driver.find_element_by_css_selector(
        ".control.button2.button2_view_classic.button2_size_l.button2_theme_action.button2_width_max.button2_type_submit.passp-form-button").click()
    sleep(1)

def post_to_yandex_zen(post):

    print(post.title, post.gif_url, post.text)
    # exit(0)

    #Auth
    if driver is None:
        authentificate_in_yandex_zen()

    #Preparing
    # driver.get("https://zen.yandex.ru/profile/editor/id/5c8ce13954593600b40ba8e4")
    driver.get("https://zen.yandex.ru/profile/editor/id/5c8ce13954593600b40ba8e4")
    sleep(1)

    driver.find_element_by_css_selector(".header__add-button").click()
    sleep(1)
    driver.find_element_by_css_selector(".header__popup-add-button_article").click()
    sleep(1)
    try:
        close_btn = driver.find_element_by_css_selector(".close-cross.close-cross_black.close-cross_size_s.help-popup__close-cross")
        if close_btn is not None:
            close_btn.click()
    except Exception as e:
        print(str(e))
    sleep(1)

    # Article creation
    actions = ActionChains(driver)
    actions.send_keys(post.text)
    actions.perform()
    sleep(1)

    title_field = driver.find_element_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
    title_field.click()
    sleep(1)
    actions = ActionChains(driver)
    actions.send_keys(post.title)
    actions.perform()
    sleep(1)

    attachment_button = driver.find_element_by_css_selector(".side-button_logo_image")
    attachment_button.click()
    sleep(1)

    link_field = driver.find_element_by_css_selector(".image-popup__url-input")
    pyperclip.copy(post.gif_url)
    actions = ActionChains(driver)
    actions.send_keys(Keys.SHIFT, Keys.INSERT)
    actions.perform()
    sleep(1)

    try:
        link_field = driver.find_element_by_css_selector(".image-popup__url-input")
        pyperclip.copy(post.gif_url)
        actions = ActionChains(driver)
        actions.send_keys(Keys.SHIFT, Keys.INSERT)
        actions.perform()
    except Exception as e:
        print("Worked before")

    sleep(30)


def multiple_post_to_yandex_zen(posts):

    print(f"Posting {len(posts)} posts")
    #preparing Data
    tags = {}
    for post in posts:
        for tag in post.tags:
            if tag not in tags.keys():
                tags[tag] = 1
            else:
                tags[tag] += 1
        # print(post.title, post.gif_url, post.text, post.tags)
    tags = sorted(tags.items(), key=lambda kv: -kv[1])
    if len(tags) > 10:
        tags = tags[:10]

    title = "Подборка интересных гифок на вечер"
    subtitle = f"Сегодня у нас {tags[1][0]}, {tags[2][0]}, {tags[3][0]} и {tags[4][0]}!"

    print(subtitle)

    # Auth
    if driver is None:
        authentificate_in_yandex_zen()

    # Preparing
    # driver.get("https://zen.yandex.ru/profile/editor/id/5c8ce13954593600b40ba8e4")
    driver.get("https://zen.yandex.ru/profile/editor/id/5c8ce13954593600b40ba8e4")
    sleep(1.1)

    driver.find_element_by_css_selector(".header__add-button").click()
    sleep(1.2)
    driver.find_element_by_css_selector(".header__popup-add-button_article").click()
    sleep(1.4)
    try:
        close_btn = driver.find_element_by_css_selector(
            ".close-cross.close-cross_black.close-cross_size_s.help-popup__close-cross")
        if close_btn is not None:
            close_btn.click()
    except Exception as e:
        print(str(e))
    sleep(1)

    # Article creation
    # actions = ActionChains(driver)
    # actions.send_keys(subtitle)
    # actions.perform()
    # sleep(2.1)

    title_field = driver.find_element_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
    title_field.click()
    sleep(1.5)
    actions = ActionChains(driver)
    actions.send_keys(title)
    actions.perform()
    sleep(1.1)

    first = True
    attachment_button = None

    for post in posts:
        # if first:
        #     sleep(1)
        #     editor = driver.find_element_by_css_selector(".zen-editor-block-paragraph")
        #     editor.click()
        #     sleep(1)
        #     actions = ActionChains(driver)
        #     actions.send_keys(post.title)
        #     actions.send_keys(Keys.RETURN)
        #     actions.perform()
        #     first = False
        #     sleep(1)
        # else:
        #     sleep(1)
        #     actions = ActionChains(driver)
        #     actions.send_keys(post.title)
        #     actions.send_keys(Keys.RETURN)
        #     actions.perform()
        #     sleep(1)
        #     last_par = driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")[-1]
        #     last_par.click()
        #     last_par.send_keys(Keys.RETURN)
        #     sleep(1)
        #     actions = ActionChains(driver)
        #     actions.send_keys(Keys.RETURN)
        #     actions.perform()
        #     sleep(2)

        if attachment_button is None:
            attachment_button = driver.find_element_by_css_selector(".side-button_logo_image")
        attachment_button.click()
        sleep(1)

        link_field = driver.find_element_by_css_selector(".image-popup__url-input")
        pyperclip.copy(post.gif_url)
        actions = ActionChains(driver)
        actions.send_keys(Keys.SHIFT, Keys.INSERT)
        actions.perform()
        sleep(1)

        try:
            while True:
                link_field = driver.find_element_by_css_selector(".image-popup__url-input")
                pyperclip.copy(post.gif_url)
                actions = ActionChains(driver)
                actions.send_keys(Keys.SHIFT, Keys.INSERT)
                actions.perform()
                sleep(1)
        except Exception as e:
            print("Worked before")

        sleep(5)

    for i in range(len(posts)):
        print(f"Going up {i}")
        actions = ActionChains(driver)
        actions.send_keys(Keys.ARROW_UP)
        actions.send_keys(Keys.ARROW_UP)
        actions.send_keys(Keys.ARROW_UP)
        actions.send_keys(str(i))
        actions.perform()
        sleep(1)


def main():

    global LastPostDay

    # if PostOnStartUp:
    #     latest_post_url = ""
    # else:
    #     latest_post_url = get_list_of_pikabu_urls(PikabuMainUrl)[0]


    # for link in reversed(get_list_of_pikabu_urls()):
    #     print(link)
    #     p = Post.from_url(link)
    #     post_gif(p)
    # exit(0)

    # for day in range(3850, 3928):
    #     print("Day: " + str(day))
    #     link = f"https://pikabu.ru/search?t=Гифка%2CЖивотные&r=7&d={day - 1}&D={day}"
    #     best_link_of_the_day = get_list_of_pikabu_urls(link)[0]
    #     p = Post.from_url(best_link_of_the_day)
    #     if best_link_of_the_day in postedLinks or p is None:
    #         continue
    #     postedLinks.append(best_link_of_the_day)
    #     # print(best_link_of_the_day)
    #     post_to_yandex_zen(p)
    #     # res = post_gif(p)
    #     # if res:
    #     #     sleep(45)
    #
    # driver.close()
    # exit(0)

    while True:

        t = round(datetime.now().timestamp())
        day = t // (24 * 60 * 60)
        offset = t % (24 * 60 * 60)
        print(day, offset)
        if day > LastPostDay and offset > ArticlePostTimeUtcOffsetSeconds:
            print("It's time to post!")
            LastPostDay = day
            try:
                pikaDay = day - 17980 + 4101
                raiting = 6
                pikaUrl = f"https://pikabu.ru/tag/Гифка?r={raiting}&d={pikaDay}&D={pikaDay}"
                posts = get_multiple_posts(pikaUrl)
                multiple_post_to_yandex_zen(posts)

            except Exception as ex:
                print('main: exception: ' + str(ex))
        print("Waiting...")
        sleep(NewsCheckPeriod)


if __name__ == '__main__':
    main()
    # post_to_yandex_zen(None)
