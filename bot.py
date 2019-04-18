import telegram
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
from datetime import datetime
import logging
from postClass import *
import bs4
import random

# from tendo import singleton
# me = singleton.SingleInstance()

chrome_options = Options()
# chrome_options.add_argument("--headless")

PostOnStartUp = False
NewsCheckPeriod = 5 * 60    # seconds

ArticlePostTimeMoscowOffset = 19.00  # Hours 19:00 Moscow UTC+3
ArticlePostTimeUtcOffsetSeconds = (ArticlePostTimeMoscowOffset - 3) * 60 * 60

LastPostDay = 0

TOKEN = '582293326:AAG-1JSt4WHDXE9kMu4KFs7pghcIWKFdFE0'

postedLinksFilename = "posted.csv"
postedLinks = []

tag_black_list = ['reddit', '[моё]', 'длиннопост']

titles = ["Подборка интересных гифок на вечер",
          "Самые интересные гифки за сегодня",
          "Свежая подборка гифок",
          "Итоги дня в гифках",
          "Гифки это божественно!",
          "Подборка свежайших гифок"]

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
        amount = len(post.findAll("div", {"class": "player"}))
        logging.debug(f"Players amount: {amount}")
        if amount != 1:
            logging.warning(f"Post dropped. Wrong player ammount {amount}")
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

        if 'часть' in title.lower() or 'фотографии' in title.lower():
            logging.warning(f"Часть. Post dropped")
            continue

        tags = [tag.text.lower() for tag in post.findAll("a", {"class": "tags__tag"})]
        parsed_posts.append(Post(title, gif_url=gif_url, tags=tags))

    return parsed_posts


def authentificate_in_yandex_zen(driver = None):

    login = "krupnik35"
    print(f"Password for {login}: ")
    password = "Klazklaz37"  # input()

    if driver is None:
        driver = webdriver.Chrome(options=chrome_options)

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


def add_title(driver, title):
    # Title
    title_field = driver.find_element_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
    title_field.click()
    sleep(1.5)
    actions = ActionChains(driver)
    actions.reset_actions()
    actions.send_keys(title)
    actions.perform()
    sleep(1.1)


def create_new_paragraph(driver, force=False):
    # Paragraph
    fields = driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
    num_before = len(fields)
    print(num_before)

    last_field = fields[-1]
    # try:
    #     last_field.click()
    # except Exception:
    #     pass

    if last_field.text != "" or force:
        print("Creating new paragraph")
        actions = ActionChains(driver)
        actions.reset_actions()
        actions.move_to_element(last_field)
        actions.click()
        actions.release()
        actions.pause(0.5)
        actions.send_keys(Keys.END)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        fields = driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
        last_field = fields[-1]

        num_after = len(fields)

        if last_field.text == "" and num_after > num_before:
            print("Success!")
        else:
            print("Fail!")


def add_text_paragraph(driver, text):
    create_new_paragraph(driver)

    fields = driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
    #     fields = driver.find_elements_by_css_selector(".zen-editor-block.zen-editor-block-paragraph")
    last_field = fields[-1]
    try:
        last_field.click()
    except Exception:
        pass

    actions = ActionChains(driver)
    actions.reset_actions()
    actions.move_to_element(last_field)
    actions.click()
    actions.release()
    actions.pause(0.5)
    actions.send_keys(text)
    actions.perform()


# Gif
def add_gif_paragraph(driver, url):
    sleep(1)
    before_images_num = len(driver.find_elements_by_css_selector(".zen-editor-block-image__image"))

    attachment_button = None
    try:
        create_new_paragraph(driver, True)
        sleep(3)
        attachment_button = driver.find_element_by_css_selector(".side-button.side-button_logo_image")
        if attachment_button is None:
            create_new_paragraph(driver, True)
            sleep(1)
            attachment_button = driver.find_element_by_css_selector(".side-button.side-button_logo_image")
        # print(f"Att button: {attachment_button}")
        attachment_button.click()
        sleep(1)
    except Exception as e:
        print(f"Can't find or create attachment button {str(e)}")
        return False

    if attachment_button is None:
        print("Can't find or create attachment button")
        return False

    link_field = driver.find_element_by_css_selector(".image-popup__url-input")
    pyperclip.copy(url)
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.INSERT).key_up(Keys.SHIFT).perform()
    sleep(3)

    try:
        while True:

            images_num = len(driver.find_elements_by_css_selector(".zen-editor-block-image__image"))
            if images_num > before_images_num:
                print("Posted!")
                return True

            print("Trying to post")
            link_field = driver.find_element_by_css_selector(".image-popup__url-input")
            link_field.click()
            pyperclip.copy(url)
            ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.INSERT).key_up(Keys.SHIFT).perform()
            sleep(1)

    except Exception as e:
        print("Worked before")

    return False


def add_gif_caption(driver, index, caption):
    captions = driver.find_elements_by_css_selector(".zen-editor-block-image__caption")
    # print(f"Captions num: {len(captions)}")

    pyperclip.copy(caption)

    print(f"Creating caption {index} {caption}")
    ActionChains(driver).move_to_element(captions[index]).pause(2).move_to_element(
        captions[index]).pause(2).click().perform()
    sleep(5)
    # ActionChains(driver).send_keys(Keys.SHIFT, Keys.INSERT).perform()
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.INSERT).key_up(Keys.SHIFT).perform()
    sleep(1)


def publish(driver, tags, description):
    publish_button = driver.find_element_by_css_selector(".editor-header__edit-btn")
    ActionChains(driver).move_to_element(publish_button).click().perform()

    sleep(1)

    description_input = driver.find_element_by_name("covers[0].snippet")

    while description_input.text != "":
        ActionChains(driver).move_to_element(description_input).click().send_keys(
            Keys.BACK_SPACE).send_keys(Keys.DELETE).perform()

    sleep(1)
    ActionChains(driver).move_to_element(description_input).click().send_keys(description).perform()

    sleep(1)

    tags_input = driver.find_element_by_css_selector(".ui-lib-tag-input__input")
    ActionChains(driver).move_to_element(tags_input).click().send_keys(",".join(tags)).perform()

    sleep(1)

    driver.find_element_by_css_selector(".publication-settings-actions__action").click()

    sleep(5)
    #
    # submit_button = driver.find_element_by_css_selector(".publication-settings-actions__action").click()
    # if submit_button is not None:
    #     print("Trying to submit again")
    #     ActionChains(driver).move_to_element(submit_button).pause(1).click().pause(1).perform()


def scroll_to_top(driver):
    # ActionChains(driver).key_down(Keys.PAGE_UP).pause(5).key_up(Keys.PAGE_UP).perform()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys(Keys.HOME).key_up(Keys.CONTROL).perform()
    sleep(5)


def multiple_post_to_yandex_zen(posts):

    global driver

    print(f"Posting {len(posts)} posts")
    tags = {}
    for post in posts:
        for tag in post.tags:
            if tag not in tags.keys():
                if tag not in tag_black_list:
                    tags[tag] = 1
                else:
                    print(f"Tag {tag} from black list dropped")
            else:
                tags[tag] += 1
    tags = sorted(tags.items(), key=lambda kv: -kv[1])
    if len(tags) > 10:
        tags = tags[:10]

    title = random.choice(titles)
    subtitle = f"Сегодня у нас {tags[1][0]}, {tags[2][0]}, {tags[3][0]} и {tags[4][0]}!"

    tags = [tag[0] for tag in tags]

    print(subtitle)

    if driver is None:
        driver = webdriver.Chrome(options=chrome_options)
        authentificate_in_yandex_zen(driver)

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

    add_title(driver, title)
    sleep(1)
    add_text_paragraph(driver, subtitle)
    sleep(1)

    failed_posts = []

    for post in posts:
        if not add_gif_paragraph(driver, post.gif_url):
            print(f"Posting failed. Post {post.title} removed")
            failed_posts.append(post)
            continue
        sleep(5)

    for fail in failed_posts:
        posts.remove(fail)

    print(f"Posted: {len(posts)}")
    print(f"Failed: {len(failed_posts)}")

    scroll_to_top(driver)

    for post in posts:
        add_gif_caption(driver, posts.index(post), post.title)
        sleep(3)

    publish(driver, tags, subtitle)

    driver.close()


def main():

    global LastPostDay

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
