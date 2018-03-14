import telegram
from time import sleep

from postClass import *

# from tendo import singleton
# me = singleton.SingleInstance()

TOKEN = '582293326:AAG-1JSt4WHDXE9kMu4KFs7pghcIWKFdFE0'
ChannelId = -1001392228565
BoldPrefix = '<b>'
BoldPostfix = '</b>'

bot = telegram.Bot(token=TOKEN)

def post_text(post):

    message = BoldPrefix
    message += post.header
    message += BoldPostfix + '\n\n'
    message += post.body

    try:
        bot.send_message(ChannelId, text=message, parse_mode='HTML')
    except Exception as ex:
        print('post_text: exception: ' + str(ex))


def post_picture(picture_file, caption=''):
    try:
        bot.sendPhoto(ChannelId, photo=open(picture_file, 'rb'), caption=caption)
    except Exception as ex:
        print('post_picture: failed to send photo: ' + str(ex))


def get_new_text():
    return ''


def main():
    post_text(Post("Header", "Text"))
    # while True:
    #     try:
    #         text = get_new_text()
    #         if text != '':
    #             post_text(text)
    #     except Exception as ex:
    #         print('main: exception: ' + str(ex))
    #     sleep(10)


if __name__ == '__main__':
    main()
