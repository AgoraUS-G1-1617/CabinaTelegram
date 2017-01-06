# -*- encoding: utf-8 -*-

import time

import requests
from telebot import types

import variables
from src.utils import Utils
from src.votacion import Votacion
from src.votacion import Panel
import json
import urllib.request as ur
import urllib.parse as par
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
                       '/votaciones - ✉️ Muestra las votaciones existentes\n' \
                       '/verVotaciones - ✉️ Muestra las votaciones existentes\n' \
                       '/recontarVotacion - ✉️ Muestra el resultado de una votación\n' \
                       '/compartir - 🗣 Muestra panel para compartir votaciones\n' \
                       '/login - 🔓 Inicia sesión con una cuenta de authb\n' \
                       '/logout - 🔒 Cierra sesión' % name
                bot.send_photo(chat_id, 'http://imgur.com/VesqBnN.png')
            bot.reply_to(message, text)


        # VER TODAS LAS VOTACIONES DEL SISTEMA
        @bot.message_handler(commands=['verVotaciones'])
        def ver_votaciones(message):
            try:
                url = 'https://recuento.agoraus1.egc.duckdns.org/api/verVotaciones'

                html = ur.urlopen(url).read()
                data = json.loads(html.decode('utf-8'))
                diccionario_votaciones = data.get('votaciones')
                print(diccionario_votaciones)

                texto = '*Votaciones del sistema:*\n'
                for votacion in diccionario_votaciones:
                    print(votacion)
                    texto += 'votacion:\n'
                    for campo, valor in votacion.items():
                        ## texto+=campo
                        texto += ': '
                        texto += str(valor)
                bot.reply_to(message, texto)

            except Exception as e:
                bot.reply_to(message, e)


        # VER RESULTADO (RECUENTO) DE UNA VOTACION EN PARTICULAR
        # ACTUALMENTE NO SE LE PUEDEN PASAR VOTACIONES EN PARTICULAR, SOLO FUNCIONA CON UNA FIJA
        @bot.message_handler(commands=['recontarVotacion'])
        def recuento_votacion(message):
            try:
                result = 'Recuento de la votación:'
                url = 'https://recuento.agoraus1.egc.duckdns.org/api/recontarVotacion?idVotacion=4'

                html = ur.urlopen(url).read()
                data = json.loads(html.decode('utf-8'))
                lista_preguntas = data.get('preguntas')

                # pregunta es un diccionario
                for pregunta in lista_preguntas:
                    for preg, respuestas in pregunta.items():
                        if preg == ('texto_pregunta'):
                            result += '\n\n' + str(pregunta['texto_pregunta'])
                            print('Esto es una pregunta: ' + str(pregunta['texto_pregunta']))
                        elif isinstance(respuestas, list):
                            for opcion in respuestas:
                                for clave, valor in opcion.items():
                                    if clave == ('texto_opcion'):
                                        result += '\n' + str(opcion['texto_opcion'])
                                        print('Opcion: ' + str(opcion['texto_opcion']))
                                    if clave == ('votos'):
                                        result += ' votos: ' + str(opcion['votos'])
                                        print('Numero de votos: ' + str(opcion['votos']))

                bot.reply_to(message, result)
            except Exception as e:
                bot.reply_to(message, e)


        @bot.message_handler(commands=['login'])
        def login(message):
            chat_id = message.chat.id
            user_id = message.from_user.id
            url = variables.login_link + str(user_id)
            url_registro = variables.register_link
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Iniciar sesión', url=url))
            markup.add(types.InlineKeyboardButton('Crear cuenta', url=url_registro))
            bot.send_message(chat_id, 'Inicia sesión a través de este enlace:\n', reply_markup=markup)

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
        def responder(call):
            user_id = call.from_user.id
            votacion = variables.sesion[user_id]
            votacion.responder_pregunta(call)


        @bot.message_handler(commands=['votaciones'])
        def mis_votaciones(message):
            user_id = message.from_user.id
            # votaciones = utils.get_votaciones(user_id)
            text = '*Votaciones:*\n'
            # for votacion in votaciones:
            #     text += '\n🔹 %s /votacion\_%d' % (votacion[0], votacion[3])

            # DE PRUEBA
            for i in range(1, 5):
                text += '\n🔹 Ejemplo /votacion\_%d' % i
            bot.reply_to(message, text, parse_mode='Markdown')

        @bot.message_handler(regexp='^(/votacion_)\d+')
        def info_votacion(message):
            chat_id = message.chat.id
            votacion_id = int(message.text.split('_')[1])
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Comenzar votación", callback_data="ID%i" % votacion_id))
            markup.add(types.InlineKeyboardButton("Compartir", switch_inline_query="misvotaciones"))
            bot.send_message(chat_id, "Resultados:\n\nEjemplo 1 -> 0 votos\nEjemplo 2 -> 0 votos", reply_markup=markup)

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
                votacion_id = int(call.data.split('ID')[1])
                votacion = Votacion()
                votacion.get_votacion_api(votacion_id)
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
