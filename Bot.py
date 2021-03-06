import json
import socket
from time import time

import requests

# import forecast
# import camera
import config
import funcs
import reddit_handler
import Weather

TOKEN = config.token
CLIENT_ID = config.client_id
SECRET = config.secret
USER_AGENT = config.user_agent


class Bot:

    def __init__(self):

        self.__url = 'https://api.telegram.org/bot%s/' % TOKEN
        self.__multireddit = funcs.get_subreddits()
        self.__offset = 0
        self.__last_update = 0

        # stats
        self.__start_time = time()
        self.__messages_sent = 0

        # meme
        self.__link = ""
        self.__title = ""
        self.__sub = ""
        self.new_meme()

        # weather
        self.__weather = Weather.Weather()

    def get_updates(self):

        try:
            updates = json.loads(requests.get(self.__url + 'getUpdates?offset=' + str(self.__offset)).content)
        except socket.gaierror:
            print(
                "\n\n\n gaierror! \n\n\n"
            )

            return
            # updates = json.loads(requests.get(self.__url + 'getUpdates').content)

        # hotfixing
        if 'result' not in updates:
            return

        for update in updates['result']:

            # Refresh this
            if self.__last_update < update['update_id']:
                self.__last_update = update['update_id']

            try:
                # Don't process old updates.
                if time() - update['message']['date'] < 10:
                    self.process_update(update)

            # Some updates don't contain 'message'.
            except KeyError:
                pass

            # New offset to automatically clear the queue at tg server-side
            self.__offset = update['update_id'] + 1

    def send_message(self, update, message):

        chat_id = update['message']['chat']['id']
        params = dict(chat_id=chat_id, text=message, disable_notification=True)
        requests.get(self.__url + 'sendMessage', params=params)
        self.__messages_sent += 1

    def process_update(self, update):

        if not update['message']['text']:
            return

        # A command interpreter of sorts - all used Telegram bot commands should be specified here
        msg = update['message']['text']

        if '/help' in msg:
            self.send_help(update)

        elif '/meme' in msg:
            self.send_meme(update)

        elif '/stats' in msg:
            self.stats(update)

        elif '/keli' in msg:
            self.send_weather(update)

        elif '/kaannos' in msg:
            if 'reply_to_message' in update['message'].keys():
                self.translate(update)
            else:
                message = '/kaannos: vastaa johonkin viestiin komennolla ' \
                          '/kaannos. Ei toimi muiden bottien viesteihin.'
                self.send_message(update, message)

        elif '/tumppi' in msg:
            self.send_tumppi(update)

        elif '/ennuste' in msg:
            self.send_forecast(update)

        elif '/ping' in msg:
            self.send_ping(update)

        elif '/uwu' in msg:
            self.send_cancer(update)

    #                                  method bodies defined below.

    def send_meme(self, update):

        if update['message']['entities'][0]['type'] == 'bot_command':

            message = 'r/' + self.__sub + ':' '\n' + self.__title + '\n' + self.__link
            self.send_message(update, message)
            # Refresh meme
            self.new_meme()

    def send_help(self, update):

        if update['message']['from']['is_bot'] is False:
            message = funcs.decide(update['message']['text'])
            self.send_message(update, message)

    def new_meme(self):
        # Refresh the meme
        try:
            self.__link, self.__title, self.__sub = reddit_handler.get_url(
                multireddit=self.__multireddit, client_id=CLIENT_ID, client_secret=SECRET, user_agent=USER_AGENT
            )
        except TypeError:
            self.new_meme()

    def stats(self, update):

        message = funcs.uptime(time() - self.__start_time)
        message = f"{message} \n\n{self.__messages_sent} messages"

        self.send_message(update, message)

    def translate(self, update):

        message = funcs.scramble(update['message']['reply_to_message']['text'])
        self.send_message(update, message)

    def send_weather(self, update):

        message = self.__weather.get_message()
        self.send_message(update, message)

    def send_tumppi(self, update):

        """
        if update['message']['chat']['id'] in config.friendly:

            try:
                camera.new_image()  # refresh 'tumppi.jpeg'

                files = {'photo': ('tumppi.jpeg', open('tumppi.jpeg', 'rb'), 'photo/jpeg', {'Expires': '0'})}

                chat_id = update['message']['chat']['id']
                requests.post(self.__url + 'sendPhoto?', params=dict(chat_id=chat_id), files=files)

            except:  # TODO:
                self.send_message(update, 'Hups! Tämä toiminto ei ole käytössä.')

        else:
            self.send_message(update, 'Hups! Tämä toiminto ei ole käytössä.')
        """
        self.send_message(update=update, message='Hups! Tämä toiminto ei ole käytössä.')

    def send_forecast(self, update):

        try:
            forecast.forecast()  # refresh 'ennuste.png'

            files = {'photo': ('ennuste.png', open('ennuste.png', 'rb'), 'photo/png', {'Expires': '0'})}

            chat_id = update['message']['chat']['id']
            requests.post(self.__url + 'sendPhoto?', params=dict(chat_id=chat_id), files=files)

        except:
            return

    def send_ping(self, update):

        message = 'pong'
        self.send_message(update, message)

    def send_cancer(self, update):

        message = funcs.uwu(update['message']['reply_to_message']['text'])
        self.send_message(update, message)
