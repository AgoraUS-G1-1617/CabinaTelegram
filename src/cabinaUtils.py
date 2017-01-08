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

class CabinaUtils:

    def send_welcome(self, message):
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
                   '/votacion - 📝 Crea una votación\n' \
                   '/votaciones - ✉️ Muestra las votaciones existentes\n' \
                   '/recontarVotacion - ✉️ Muestra el resultado de una votación\n' \
                   '/compartir - 🗣 Muestra panel para compartir votaciones\n' \
                   '/login - 🔓 Inicia sesión con una cuenta de authb\n' \
                   '/logout - 🔒 Cierra sesión' % name
            bot.send_photo(chat_id, 'http://imgur.com/VesqBnN.png')
        bot.reply_to(message, text)

    def cancel(self, call):
        chat_id = call.message.chat.id
        bot.send_message(chat_id, '❌ Operación cancelada')

    # VER TODAS LAS VOTACIONES DEL SISTEMA
    def ver_votaciones(self, message):
        try:
            url = 'https://beta.recuento.agoraus1.egc.duckdns.org/api/verVotaciones'
            html = ur.urlopen(url).read()
            data = json.loads(html.decode('utf-8'))
            diccionario_votaciones = data.get('votaciones')
            texto = '*Votaciones del sistema:*\n'
            for votacion in diccionario_votaciones:
                texto += '\n🔹 /votacion\_%d %s' % (votacion['id_votacion'], votacion['titulo'])
            bot.send_message(message.chat.id, texto, parse_mode='Markdown')
            return texto
        except Exception:
            errormsg = 'Ha habido algun problema al procesar la peticion'
            bot.send_message(message.chat.id, errormsg)
            return errormsg

    # VER RESULTADO (RECUENTO) DE UNA VOTACION EN PARTICULAR
    # ACTUALMENTE NO SE LE PUEDEN PASAR VOTACIONES EN PARTICULAR, SOLO FUNCIONA CON UNA FIJA
    def recuento_votacion(self, message):
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

            bot.send_message(message.chat.id, result)
            return result
        except Exception:
            errormsg = 'No se puede recontar la votacion porque no esta cerrada'
            bot.send_message(message.chat.id, errormsg)
            return errormsg

    def login(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        url = variables.login_link + str(user_id)
        url_registro = variables.register_link
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Iniciar sesión', url=url))
        markup.add(types.InlineKeyboardButton('Crear cuenta', url=url_registro))
        bot.send_message(chat_id, 'Inicia sesión a través de este enlace:\n', reply_markup=markup)

    def logout(self, message):
        user_id = message.from_user.id
        logged = utils.logout(user_id)
        if not logged:
            text = 'Has cerrado sesión correctamente.'
        else:
            text = 'No hemos podido cerrar sesión.'
        bot.reply_to(message, text)

    def crear_votacion(self, message):
        user_id = message.from_user.id
        votacion = Votacion()
        votacion.crear_votacion(message)
        variables.sesion[user_id] = votacion

    def responder(self, call):
        user_id = call.from_user.id
        votacion = variables.sesion[user_id]
        votacion.responder_pregunta(call)

    def info_votacion(self, message):
        chat_id = message.chat.id
        votacion_id = int(message.text.split('_')[1])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Comenzar votación", callback_data="ID%i" % votacion_id))
        markup.add(types.InlineKeyboardButton("Compartir", switch_inline_query="misvotaciones"))
        bot.send_message(chat_id, "Resultados:\n\nEjemplo 1 -> 0 votos\nEjemplo 2 -> 0 votos", reply_markup=markup)

    def compartir_votaciones(self, message):
        user_id = message.from_user.id
        votaciones = utils.get_votaciones(user_id)
        markup = types.InlineKeyboardMarkup()
        for votacion in votaciones:
            markup.add(types.InlineKeyboardButton(votacion[0], switch_inline_query="misvotaciones"))
        bot.send_message(message.chat.id, "Mis votaciones", reply_markup=markup)

    def query_text(self, inline_query):
        panel.query_text(inline_query)

    def callback_start_votation(self, call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        is_voted = True
        modificar_voto = False
        eliminar_voto = False
        try:
            if utils.get_logged(user_id):
                # Comprueba si el callback data indica una modificación de voto
                votacion_id = call.data.split('ID')[1]
                if votacion_id[-1] == 'M':
                    votacion_id = votacion_id[:-1]
                    modificar_voto = True
                elif votacion_id[-1] == 'E':
                    votacion_id = votacion_id[:-1]
                    eliminar_voto = True
                votacion_id = int(votacion_id)

                if is_voted and not modificar_voto and not eliminar_voto:
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    modificar_button = types.InlineKeyboardButton("Modificar", callback_data="ID%iM" % votacion_id)
                    eliminar_button = types.InlineKeyboardButton("Eliminar", callback_data="ID%iE" % votacion_id)
                    cancelar_button = types.InlineKeyboardButton("Cancelar", callback_data="CANCEL")
                    markup.add(modificar_button, eliminar_button, cancelar_button)
                    bot.send_message(chat_id, 'Ya has participado en esta votación', reply_markup=markup)
                else:
                    votacion = Votacion()
                    votacion.modificar_voto = modificar_voto
                    votacion.get_votacion_api(votacion_id)
                    variables.sesion[user_id] = votacion
                    if eliminar_voto:
                        votacion.eliminar_votos_api(call)
                    else:
                        votacion.enviar_pregunta(user_id)
            else:
                text = 'Debes iniciar sesión para votar, recuerda que puedes hacerlo con el comando /login'
                bot.send_message(chat_id, text)

        except Exception as e:
            print(e)
