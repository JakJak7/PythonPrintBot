#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from PIL import Image
from subprocess import call
import requests
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(bot, update):
  send_text(bot, update, 'Send me stickers!')

def message(bot, update):
  send_text(bot, update, 'Send me stickers!')

def send_text(bot, update, message):
  bot.send_message(chat_id=update.message.chat_id, text=message)

def photo(bot, update):
  file_id = update.message.photo[-1].file_id
  photo_file = bot.get_file(file_id)
  file_location = 'files/' + file_id + '.jpg'
  photo_file.download(file_location)
  update.message.reply_text('Printing image!')
#  print_label(file_id, '.jpg')
  r = lighten_image(file_id, '.jpg')

def sticker(bot, update):
  file_id = update.message.sticker.file_id
  sticker_file = bot.get_file(file_id)
  file_location = 'files/' + file_id + '.webp'
  sticker_file.download(file_location)
  update.message.reply_text('Printing sticker!')
  convert_webp(file_id, file_location)
#  r = print_label(file_id, '.png')
  r = lighten_image(file_id, '.png')

def convert_webp(file_id, file_location):
  call(['dwebp', file_location, '-o', 'files/' + file_id + '.png'])

def print_label(file_id, file_extension):
  url = 'http://localhost:8013/api/print/image'
  file = {'upload': open('files/' + file_id + file_extension, 'rb')}
  r = requests.post(url, files=file)
  return r.status_code == 200

def lighten_image(file_id, file_extension):
  file_path = 'files/' + file_id + file_extension
  new_file_id = file_id + '_light20'
  new_file_path = 'files/' + new_file_id + file_extension
  call(['convert', file_path, '-fill', 'white', '-colorize', '20%', new_file_path])
  return print_label(new_file_id, file_extension)


updater = Updater(token='[bot_id]:[bot_api_key]')
dp = updater.dispatcher

start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)

text_handler = MessageHandler(Filters.text, message)
dp.add_handler(text_handler)

photo_handler = MessageHandler(Filters.photo, photo)
dp.add_handler(photo_handler)

sticker_handler = MessageHandler(Filters.sticker, sticker)
dp.add_handler(sticker_handler)

updater.start_polling()
updater.idle()
