# PythonPrintBot
Telegram bot written in python, prints labels from images and stickers.

Will download all incoming images and Telegram stickers to folder named 'files', convert them to an appropiate format, and send them to Brother label printer.
I use this with my Brother QL-560 with auto-cutter feature, with 62mm endless labels only.

# Dependencies
* Python 3.5. Haven't tested with other versions.
* dwebp package. Used to convert from webp image format, which Telegram stickers are by default.
* Brother printer web service from https://github.com/tobalr/brother_ql_web running in order to print. Address and port is hardcoded in python script.
* Python Telegram bot library from https://github.com/python-telegram-bot/python-telegram-bot. Bot ID and API token are hardcoded, and need to be filled in at line 58 in bot.py.
* Python Requests library, http://docs.python-requests.org/en/master/. For making HTTP requests.
* (optional) ImageMagick package. Used to modify image before print. I noticed that anything darker than 70% would come out almost completely black, so to offset this I use the lighten_image() function to increase brightness by 20%. Call print_label() directly instead of lighten_image() to skip this step.

I forgot if PIL Image and logging libraries are required, can probably be removed.