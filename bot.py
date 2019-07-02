#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
from subprocess import call
import requests
import logging
import configparser
import json

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
    #update.message.reply_text('Printing image!')
    handle_image(bot, update, file_id, '.jpg', text)

def sticker(bot, update):
    file_id = update.message.sticker.file_id
    sticker_file = bot.get_file(file_id)
    file_location = 'files/' + file_id + '.webp'
    sticker_file.download(file_location)
    #update.message.reply_text('Printing sticker!')
    convert_webp(file_id, file_location)
    handle_image(bot, update, file_id, '.png', '20')

def handle_image(bot, update, file_id, file_extension, percentage):
    file_name = lighten_image(file_id, file_extension, percentage)
    ask_master(bot, "username:DDD", update.message.chat_id, file_name, file_id)
    #return print_label(file_name)

def convert_webp(file_id, file_location):
    call(['dwebp', file_location, '-o', 'files/' + file_id + '.png'])

def print_label(file_name):
    url = config['BOT_SECRETS']['BaseUrl'] + 'api/print/image'
    file = {'upload': open('files/' + file_name, 'rb')}
    r = requests.post(url, files=file)
    return r.status_code == 200

def lighten_image(file_id, file_extension, percentage):
    file_path = 'files/' + file_id + file_extension
    new_file_id = file_id + '_light' + percentage
    new_file_path = 'files/' + new_file_id + file_extension
    call(['convert', file_path, '-fill', 'white', '-colorize', percentage+'%', new_file_path])
    return new_file_id + file_extension

def start(bot, update):
    send_text(bot, update, 'Send me stickers!')

def message(bot, update):
    send_text(bot, update, 'Send me stickers!')

def send_text(bot, update, message):
    bot.send_message(chat_id=update.message.chat_id, text=message)

def ask_master(bot, user_name, chat_id, file_name, file_id):
    dataA = str(chat_id)+";"+file_name+";a"
    dataB = str(chat_id)+";"+file_name+";b"
    items = [[InlineKeyboardButton(text="Allow", callback_data=dataA), InlineKeyboardButton(text="Deny", callback_data=dataB)]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=items)
    message = user_name + "(" + str(chat_id) + ")"
    bot.send_photo(chat_id=chat_id, photo=file_id, caption=message, reply_markup=reply_markup)

def send_to_master(text):
    get_bot().send_message(chat_id=config['BOT_SECRETS']['MasterUserId'], text=text)

def get_bot():
    return Bot(token=config['BOT_SECRETS']['Token'])

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

def callback_handler(bot, query):
    print(query.callback_query.data)
    things = query.callback_query.data.split(';')
    if (things[2] == "a"):
        print_label(things[1])

dp.add_handler(CallbackQueryHandler(callback_handler))

def main():
    my_ip = listen_for_connection().decode('utf-8')
    print(my_ip)
    send_to_master(my_ip)
    updater.start_polling()
    updater.idle()

main()