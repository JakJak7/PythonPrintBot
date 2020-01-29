#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from subprocess import call
import requests
import logging
import configparser

from wifi_bootstrap import listen_for_connection

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def photo(update: Update, context: CallbackContext):
    #text = update.message.caption
    #if text is None:
    #    text = '20'
    file_id = update.message.photo[-1].file_id
    handle_image(update, context, file_id, False)

def sticker(update: Update, context: CallbackContext):
    file_id = update.message.sticker.file_id
    handle_image(update, context, file_id, True)

def handle_image(update: Update, context: CallbackContext, file_id, is_sticker):
    if (str(update.message.chat_id) == config['BOT_SECRETS']['MasterUserId']):
        print_label(update.message.chat_id, file_id, is_sticker)
    else:
        username = ""
        if (update.message.chat.username is None):
            if (update.message.chat.first_name is not None):
                username = update.message.chat.first_name
            if (update.message.chat.last_name is not None):
                username = username + " " + update.message.chat.last_name
        else:
            username = "@" + update.message.chat.username
        ask_master(context, username, update.message.chat_id, file_id, is_sticker)

def convert_webp(file_id, file_location):
    call(['dwebp', file_location, '-o', 'files/' + file_id + '.png'])

def ask_master(context: CallbackContext, user_name, chat_id, file_id, is_sticker):
    base_string = ("T" if is_sticker else "F")+";"+str(chat_id)
    dataA = "a;"+base_string
    dataB = "b;"+base_string

    items = [[InlineKeyboardButton(text="Approve", callback_data=dataA), InlineKeyboardButton(text="Reject", callback_data=dataB)]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=items)
    master_user_id = config['BOT_SECRETS']['MasterUserId']
    if (is_sticker):
        context.bot.send_message(chat_id=chat_id, text="Queueing sticker...")
        context.bot.send_sticker(chat_id=master_user_id, sticker=file_id)
        message = file_id+"#\nSticker from "+user_name + " (" + str(chat_id) + ")"
        context.bot.send_message(chat_id=master_user_id, text=message, reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text="Queueing photo...")
        message = user_name + " (" + str(chat_id) + ")"
        context.bot.send_photo(chat_id=master_user_id, photo=file_id, caption=message, reply_markup=reply_markup)

def print_label(chat_id, file_id, is_sticker):
    if (is_sticker):
        file_extension = '.webp'
    else:
        file_extension = '.jpg'

    file_location = 'files/' + file_id + file_extension
    image_file = get_bot().get_file(file_id)
    image_file.download(file_location)
    if (is_sticker):
        convert_webp(file_id, file_location)
        file_extension = '.png'

    file_name = lighten_image(file_id, file_extension, '20')

    if (is_sticker):
        send_text(chat_id, 'Printing sticker!')
    else:
        send_text(chat_id, 'Printing image!')

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

def start(update: Update, context: CallbackContext):
    send_text_bot(update, context, 'Send me stickers!')

def message(update: Update, context: CallbackContext):
    send_text_bot(update, context, 'Send me stickers!')

def send_text_bot(update: Update, context: CallbackContext, message):
    context.bot.send_message(chat_id=update.message.chat_id, text=message)

def send_to_master(text):
    get_bot().send_message(chat_id=config['BOT_SECRETS']['MasterUserId'], text=text)

def send_text(chat_id, message):
    get_bot().send_message(chat_id=chat_id, text=message)

def get_bot():
    return Bot(token=config['BOT_SECRETS']['Token'])

config = configparser.ConfigParser()
config.read('config.ini')

updater = Updater(token=config['BOT_SECRETS']['Token'], use_context=True)
dp = updater.dispatcher

start_handler = CommandHandler('start', start)
dp.add_handler(start_handler)

photo_handler = MessageHandler(Filters.photo, photo)
dp.add_handler(photo_handler)

sticker_handler = MessageHandler(Filters.sticker, sticker)
dp.add_handler(sticker_handler)

text_handler = MessageHandler(Filters.text, message)
dp.add_handler(text_handler)

def callback_handler(update: Update, context: CallbackContext):
    # hides inline buttons
    message_id = update.callback_query.message.message_id
    chat_id = update.callback_query.message.chat_id
    context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id)

    things = update.callback_query.data.split(';')

    is_approved = things[0] == "a"
    if (is_approved):
        prefix = "Approved! "
    else:
        prefix = "Rejected! "

    sender_chat_id = things[2]
    is_sticker = things[1] == "T"
    if (is_sticker):
        file_id = update.callback_query.message.text.split('#')[0]
        message = prefix + update.callback_query.message.text
        context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=message)
    else:
        file_id = update.callback_query.message.photo[-1].file_id
        message = prefix + update.callback_query.message.caption
        context.bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=message)

    if (is_approved):
        print_label(sender_chat_id, file_id, is_sticker)

dp.add_handler(CallbackQueryHandler(callback_handler))

def main():
    my_ip = listen_for_connection().decode('utf-8')
    print(my_ip)
    send_to_master(my_ip)
    updater.start_polling()
    updater.idle()

main()
