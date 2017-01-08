# -*- encoding: utf-8 -*-

import time

import variables
from database import create_database
from src.utils import Utils
from src.votacion import Panel
from src.cabinaUtils import CabinaUtils

bot = variables.bot

utils = Utils()
panel = Panel()
cabinaUtils = CabinaUtils()

while True:
    try:
        @bot.message_handler(commands=['help', 'start'])
        def send_welcome(message):
            cabinaUtils.send_welcome(message)

        @bot.callback_query_handler(func=lambda call: call.data == 'CANCEL')
        def responder(call):
            cabinaUtils.cancel(call)

        @bot.message_handler(commands=['votaciones'])
        def ver_votaciones(message):
            cabinaUtils.ver_votaciones(message)

        @bot.message_handler(commands=['recontarVotacion'])
        def recuento_votacion(message):
            cabinaUtils.recuento_votacion(message)

        @bot.message_handler(commands=['login'])
        def login(message):
            cabinaUtils.login(message)

        @bot.message_handler(commands=['logout'])
        def logout(message):
            cabinaUtils.logout(message)

        @bot.message_handler(commands=['testvote'])
        def test_vote_integration(message):
            cabinaUtils.test_vote_integration(message)

        @bot.message_handler(commands=['testdelvote'])
        def test_delvote_integration(message):
            cabinaUtils.test_delvote_integration(message)

        @bot.message_handler(commands=['votacion'])
        def crear_votacion(message):
            cabinaUtils.crear_votacion(message)

        @bot.callback_query_handler(func=lambda call: call.data[:2] != 'ID' and call.data != 'CANCEL')
        def responder(call):
            cabinaUtils.responder(call)

        @bot.message_handler(regexp='^(/votacion_)\d+')
        def info_votacion(message):
            cabinaUtils.info_votacion(message)

        @bot.message_handler(commands=['compartir'])
        def compartir_votaciones(message):
            cabinaUtils.compartir_votaciones(message)

        @bot.inline_handler(func=lambda m: True)
        def query_text(inline_query):
            cabinaUtils.query_text(inline_query)

        @bot.callback_query_handler(func=lambda call: call.data[:2] == 'ID')
        def callback_start_votation(call):
            cabinaUtils.callback_start_votation(call)

        def main():
            try:
                create_database
            except Exception as exception:
                bot.send_message('Error: %s' % exception)

        if __name__ == '__main__':
            main()


        bot.polling(none_stop=True)

    except Exception as e:
        print('Error: %s\nReiniciando en 10 seg' % e)
        time.sleep(10)
