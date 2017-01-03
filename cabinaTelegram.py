# -*- encoding: utf-8 -*-

import time

import requests
from telebot import types

import variables
from src.utils import Utils
from src.votacion import Votacion
from src.votacion import Panel

from database import create_database

bot = variables.bot

utils = Utils()
panel = Panel()

while True:
    try:
        @bot.message_handler(commands=['help', 'start'])
        def send_welcome(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            unique_code = utils.extract_unique_code(message.text)
            try:
                name = message.from_user.first_name
            except Exception as e:
                print(e)
                name = ''

            if unique_code and utils.set_logged(user_id, unique_code):
                text = '¡Bienvenido %s, has iniciado sesión correctamente!\n' % name
            else:
                text = '¡Bienvenido %s votador!\n' \
                       'Agora US es un sistema de votación electronico que permite llevar el tradiccional' \
                       ' método de votación actual a un sistema online de forma segura.\n\n' \
                       'Este bot es una integración de dicho sistema y actualmente permite:\n' \
                       '/testvote - 🔏 Vota en una encuesta test\n' \
                       '/testdelvote - 🔏 Eliminar voto en una encuesta test\n' \
                       '/votacion - 📝 Crea una votación\n' \
                       '/misvotaciones - Muestra mis votaciones creadas\n' \
                       '/compartir - Muestra panel para compartir votaciones' % name
                bot.send_photo(chat_id, 'http://imgur.com/VesqBnN.png')
            bot.reply_to(message, text)


        @bot.message_handler(commands=['login'])
        def login(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            url = variables.login_link + str(user_id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Invitación', url=url))
            bot.send_message(chat_id, "Incia sesión a través de este enlace:", reply_markup=markup)

        @bot.message_handler(commands=['logout'])
        def logout(message):
            user_id = message.from_user.id
            logged = utils.logout(user_id)
            if not logged:
                text = 'Has cerrado sesión correctamente.'
            else:
                text = 'No hemos podido cerrar sesión.'
            bot.reply_to(message, text)

        # EJEMPLO DE VOTE
        @bot.message_handler(commands=['testvote'])
        def test_vote_integration(message):
            try:
                voto = utils.cipher_vote("1")
                url = 'https://beta.recuento.agoraus1.egc.duckdns.org/api/emitirVoto'
                payload = {'token':'test_cabinaTelegram', 'idPregunta':'1', 'voto':voto}
                result = requests.post(url, payload)
                bot.reply_to(message, result)
            except Exception as e:
                bot.reply_to(message, e)

        # EJEMPLO DE ELIMINAR VOTE
        @bot.message_handler(commands=['testdelvote'])
        def test_delvote_integration(message):
            url = 'https://beta.recuento.agoraus1.egc.duckdns.org/api/eliminarVoto'
            payload = {'token': 'test_cabinaTelegram', 'idPregunta': '1'}
            result = requests.post(url, payload)
            bot.reply_to(message, result)

        @bot.message_handler(commands=['votacion'])
        def crear_votacion(message):
            user_id = message.from_user.id
            votacion = Votacion()
            votacion.crear_votacion(message)
            variables.sesion[user_id] = votacion

        @bot.callback_query_handler(func=lambda call: call.data[:2] != 'ID')
        def responder(message):
            user_id = message.from_user.id
            votacion = variables.sesion[user_id]
            votacion.responder_pregunta(message)


        @bot.message_handler(commands=['misvotaciones'])
        def mis_votaciones(message):
            user_id = message.from_user.id
            votaciones = utils.get_votaciones(user_id)
            text = '*Mis votaciones:*\n'
            for votacion in votaciones:
                text += '\n🔹 %s /votacion\_%d' % (votacion[0], votacion[3])
            bot.reply_to(message, text, parse_mode='Markdown')

        @bot.message_handler(regexp='^(/votacion_)\d+')
        def info_votacion(message):
            chat_id = message.chat.id
            try:
                votacion_id = message.text.split('_')[1]
                votacion = utils.get_votacion(votacion_id)
                if int(votacion[1]) != chat_id:
                    bot.send_message(chat_id, 'No tienes permiso para ver esta votación')
                else:
                    bot.send_message(chat_id, votacion)
            except Exception as e:
                bot.send_message(chat_id, 'Algo no fue bien')

        @bot.message_handler(commands=['compartir'])
        def compartir_votaciones(message):
            user_id = message.from_user.id
            votaciones = utils.get_votaciones(user_id)
            markup = types.InlineKeyboardMarkup()
            for votacion in votaciones:
                markup.add(types.InlineKeyboardButton(votacion[0], switch_inline_query="misvotaciones"))
            bot.send_message(message.chat.id, "Mis votaciones", reply_markup=markup)

        @bot.inline_handler(func=lambda m: True)
        def query_text(inline_query):
            panel.query_text(inline_query)


        @bot.callback_query_handler(func=lambda call: call.data[:2] == 'ID')
        def callback_start_votation(call):
            user_id = call.from_user.id
            try:
                votacion_id = call.data.split('ID')[1]
                votacion_datos = utils.get_votacion(votacion_id)
                votacion = Votacion()
                votacion.titulo = votacion_datos[0]
                votacion.owner_id = votacion_datos[1]
                votacion.preguntas_respuestas = votacion_datos[2]
                variables.sesion[user_id] = votacion
                votacion.enviar_pregunta(user_id)
            except Exception as e:
                print(e)

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
