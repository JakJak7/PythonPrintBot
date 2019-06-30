#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
from PIL import Image
from subprocess import call
import requests
import logging
import configparser

from wifi_bootstrap import listen_for_connection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def photo(bot, update):
    text = update.message.caption
    if text is None:
        text = '20'
    file_id = update.message.photo[-1].file_id
    photo_file = bot.get_file(file_id)
    file_location = 'files/' + file_id + '.jpg'
    photo_file.download(file_location)
    update.message.reply_text('Printing image!')
    r = lighten_image(file_id, '.jpg', text)

def sticker(bot, update):
    file_id = update.message.sticker.file_id
    sticker_file = bot.get_file(file_id)
    file_location = 'files/' + file_id + '.webp'
    sticker_file.download(file_location)
    update.message.reply_text('Printing sticker!')
    convert_webp(file_id, file_location)
    r = lighten_image(file_id, '.png', '20')

def convert_webp(file_id, file_location):
    call(['dwebp', file_location, '-o', 'files/' + file_id + '.png'])

def print_label(file_id, file_extension):
    url = config['BOT_SECRETS']['BaseUrl'] + 'api/print/image'
    file = {'upload': open('files/' + file_id + file_extension, 'rb')}
    r = requests.post(url, files=file)
    return r.status_code == 200

def lighten_image(file_id, file_extension, percentage):
    file_path = 'files/' + file_id + file_extension
    new_file_id = file_id + '_light' + percentage
    new_file_path = 'files/' + new_file_id + file_extension
    call(['convert', file_path, '-fill', 'white', '-colorize', percentage+'%', new_file_path])
    return print_label(new_file_id, file_extension)

def start(bot, update):
    send_text(bot, update, 'Send me stickers!')

def message(bot, update):
    send_text(bot, update, 'Send me stickers!')

def send_text(bot, update, message):
    bot.send_message(chat_id=update.message.chat_id, text=message)

config = configparser.ConfigParser()
config.read('config.ini')

updater = Updater(token=config['BOT_SECRETS']['Token'])
dp = updater.dispatcher

start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)

photo_handler = MessageHandler(Filters.photo, photo)
dp.add_handler(photo_handler)

sticker_handler = MessageHandler(Filters.sticker, sticker)
dp.add_handler(sticker_handler)

text_handler = MessageHandler(Filters.text, message)
dp.add_handler(text_handler)

def main():
    my_ip = listen_for_connection()
    print my_ip
    bot = Bot(token=config['BOT_SECRETS']['Token'])
    bot.send_message(chat_id=config['BOT_SECRETS']['MasterUserId'], text=my_ip)
    updater.start_polling()
    updater.idle()

main()