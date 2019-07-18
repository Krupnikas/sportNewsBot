from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import googletrans
from time import sleep

class ZenPublisher():

    driver = None
    chrome_options = None
    translator = None

    def __init__(self):
        self.chrome_options = Options()
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.translator = googletrans.Translator()

    def auth(self, login, password):

        if self.driver is None:
            self.driver = webdriver.Chrome(options=self.chrome_options)

        self.driver.get("https://passport.yandex.ru/auth?origin=zen&retpath=https%3A%2F%2Fzen.yandex.ru%2Fid%2F5c8ce13954593600b40ba8e4")
        login_field = self.driver.find_element_by_id("passp-field-login")

        login_field.send_keys(login)
        self.driver.find_element_by_css_selector(
            ".control.button2.button2_view_classic.button2_size_l.button2_theme_action.button2_width_max.button2_type_submit.passp-form-button").click()

        sleep(1)
        password_field = self.driver.find_element_by_id("passp-field-passwd")
        password_field.send_keys(password)
        self.driver.find_element_by_css_selector(
            ".control.button2.button2_view_classic.button2_size_l.button2_theme_action.button2_width_max.button2_type_submit.passp-form-button").click()
        sleep(1)

    def add_title(self, title):
        title_field = self.driver.find_element_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
        title_field.click()
        sleep(1.5)
        actions = ActionChains(self.driver)
        actions.reset_actions()
        actions.send_keys(title)
        actions.perform()
        sleep(1.1)

    def create_new_paragraph(self, force=False):
        fields = self.driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
        num_before = len(fields)
        print(num_before)

        last_field = fields[-1]

        if last_field.text != "" or force:
            print("Creating new paragraph")
            actions = ActionChains(self.driver)
            actions.reset_actions()
            actions.move_to_element(last_field)
            actions.click()
            actions.release()
            actions.pause(0.5)
            actions.send_keys(Keys.END)
            actions.send_keys(Keys.CONTROL, Keys.END)
            actions.pause(0.5)
            actions.send_keys(Keys.SPACE)
            actions.send_keys(Keys.RETURN)
            actions.pause(1.5)
            actions.perform()
            fields = self.driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
            last_field = fields[-1]

            num_after = len(fields)

            if last_field.text == "" and num_after > num_before:
                print("Success!")
            else:
                print("Fail!")

    def add_text_paragraph(self, text):
        self.create_new_paragraph()

        fields = self.driver.find_elements_by_css_selector(".public-DraftStyleDefault-block.public-DraftStyleDefault-ltr")
        last_field = fields[-1]
        try:
            last_field.click()
        except Exception:
            pass

        actions = ActionChains(self.driver)
        actions.reset_actions()
        actions.move_to_element(last_field)
        actions.click()
        actions.release()
        actions.pause(0.5)
        actions.send_keys(text)
        actions.perform()

    def add_image_paragraph(self, url):
        sleep(1)
        before_images_num = len(self.driver.find_elements_by_css_selector(".zen-editor-block-image__image"))

        attachment_button = None
        try:
            attachment_button = self.driver.find_element_by_css_selector(".side-button.side-button_logo_image")
            if attachment_button is None:
                self.create_new_paragraph(True)
                sleep(1)
                attachment_button = self.driver.find_element_by_css_selector(".side-button.side-button_logo_image")
            # print(f"Att button: {attachment_button}")
            attachment_button.click()
            sleep(1)
        except Exception as e:
            print(f"Can't find or create attachment button {str(e)}")
            return False

        if attachment_button is None:
            print("Can't find or create attachment button")
            return False

        link_field = self.driver.find_element_by_css_selector(".image-popup__url-input")
        pyperclip.copy(url)
        ActionChains(self.driver).key_down(Keys.SHIFT).send_keys(Keys.INSERT).key_up(Keys.SHIFT).perform()
        sleep(3)

        try:
            while True:

                images_num = len(self.driver.find_elements_by_css_selector(".zen-editor-block-image__image"))
                if images_num > before_images_num:
                    print("Posted!")
                    return True

                print("Trying to post")
                link_field = self.driver.find_element_by_css_selector(".image-popup__url-input")
                link_field.click()
                pyperclip.copy(url)
                ActionChains(self.driver).key_down(Keys.SHIFT).send_keys(Keys.INSERT).key_up(Keys.SHIFT).perform()
                sleep(1)

        except Exception as e:
            print("Worked before")

        return False

    def createNewArticle(self, editor_link):
        self.driver.get(editor_link)
        sleep(1.1)

        self.driver.find_element_by_css_selector(".header__add-button").click()
        sleep(1.2)
        self.driver.find_element_by_css_selector(".header__popup-add-button_article").click()
        sleep(1.4)
        try:
            close_btn = self.driver.find_element_by_css_selector(
                ".close-cross.close-cross_black.close-cross_size_s.help-popup__close-cross")
            if close_btn is not None:
                close_btn.click()
        except Exception as e:
            print(str(e))
        sleep(1)

    def fillArticle(self, article):
        title = self.translator.translate(article.title, dest='ru').text
        self.add_title(title)
        self.add_image_paragraph(article.top_image)
        for paragraph in article.text.split('\n')[:-1]:
            text  = self.translator.translate(paragraph,  dest='ru').text
            if 'WIRED' not in text:
                self.add_text_paragraph(text)


    def publish(self, tags, description):
        publish_button = self.driver.find_element_by_css_selector(".editor-header__edit-btn")
        ActionChains(self.driver).move_to_element(publish_button).click().perform()

        sleep(1)

        description_input = self.driver.find_element_by_name("covers[0].snippet")

        while description_input.text != "":
            ActionChains(self.driver).move_to_element(description_input).click().send_keys(
                Keys.BACK_SPACE).send_keys(Keys.DELETE).perform()

        sleep(2)
        print("Filling description: " + description)
        ActionChains(self.driver).move_to_element(description_input).click().pause(0.5).click().pause(0.5).send_keys(description).pause(0.5).perform()

        sleep(2)

        tags_input = self.driver.find_element_by_css_selector(".ui-lib-tag-input__input")
        print("Filling tags: " + ",".join(tags))
        ActionChains(self.driver).move_to_element(tags_input).click().pause(0.5).click().pause(0.5).send_keys(",".join(tags)).pause(0.5).perform()

        sleep(1)

        try:

            submit_button = self.driver.find_element_by_css_selector(".publication-settings-actions__action")
            submit_button.click()

            sleep(3)

            submit_button = self.driver.find_element_by_css_selector(".publication-settings-actions__action")
            ActionChains(self.driver).move_to_element(submit_button).pause(3).click().pause(1).perform()
        except Exception as e:
            print("Seems to be published...")

        sleep(5)