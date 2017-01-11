# -*- encoding: utf-8 -*-

from telebot import types
import datetime

import variables
from src.utils import Utils
from src.votacion import Votacion
from src.votacion import Panel
import json
import urllib.request as ur

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
            diccionario_votaciones = utils.obtener_votaciones()
            texto = '*Votaciones del sistema:*\n'
            for votacion in diccionario_votaciones:
                texto += '\n🔹 /votacion\_%d %s' % (votacion['id_votacion'], votacion['titulo'])
            bot.send_message(message.chat.id, texto, parse_mode='Markdown')
            return texto
        except Exception:
            errormsg = 'Ha habido algun problema al procesar la peticion'
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
        return votacion.responder_pregunta(call)

    def info_votacion(self, message):
        chat_id = message.chat.id
        votacion_id = int(message.text.split('_')[1])
        votacion = Votacion()
        votacion.get_votacion_api(votacion_id)
        text = '*%s*\n\nEstado: %s\nCP: %s\nFecha de creación: %s\nFecha de cierre: %s' % \
               (votacion.titulo, self.estado_votacion(votacion), votacion.cp, str(votacion.fecha_creacion),
                str(votacion.fecha_cierre))
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Comenzar votación", callback_data="ID%i" % votacion_id))
        markup.add(types.InlineKeyboardButton("Recontar votación", callback_data="RE%i" % votacion_id))
        markup.add(types.InlineKeyboardButton("Compartir", switch_inline_query=str(votacion_id)))
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

    def callback_recontar_votation(self, call):
        print(call.id)
        user_id = call.from_user.id
        votacion_id = int(call.data.split('RE')[1])
        try:
            result = 'Recuento de la votación *%i*:\n\n' % votacion_id
            url = variables.recuento_api + '/recontarVotacion?idVotacion=' + str(votacion_id)
            html = ur.urlopen(url).read()
            data = json.loads(html.decode('utf-8'))
            lista_preguntas = data.get('preguntas')

            # pregunta es un diccionario
            for i, pregunta in zip(range(1, len(lista_preguntas)+1), lista_preguntas):
                result += '%i. %s\n' % (i, str(pregunta['texto_pregunta']))
                for preg, respuestas in pregunta.items():
                    if isinstance(respuestas, list):
                        for opcion in respuestas:
                            for clave, valor in opcion.items():
                                if clave == ('texto_opcion'):
                                    result += '▫️ ' + str(opcion['texto_opcion'])
                                elif clave == ('votos'):
                                    result += ' - %s\n' % str(opcion['votos'])

            bot.send_message(user_id, result, parse_mode='Markdown')
            return result
        except Exception as e:
            print(str(e))
            errormsg = 'No se puede recontar la votacion porque no esta cerrada'
            if call.id != 1:
                bot.answer_callback_query(call.id, errormsg)
            return errormsg

    def estado_votacion(self, votacion):
        now = datetime.datetime.now()
        if votacion.fecha_cierre > now:
            estado = 'Abierta'
        else:
            estado = 'Cerrada'
        return estado


    def compartir_votaciones(self, message):
        try:
            diccionario_votaciones = utils.obtener_votaciones()
            markup = types.InlineKeyboardMarkup()
            for votacion in diccionario_votaciones:
                titulo = votacion['titulo']
                markup.add(types.InlineKeyboardButton(titulo, switch_inline_query=titulo))
            bot.send_message(message.chat.id, "Votaciones:", reply_markup=markup)
        except Exception as exception:
            print(str(exception))

    def query_text(self, inline_query):
        panel.query_text(inline_query)

    def callback_start_votation(self, call):
        user_id = call.from_user.id
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

                # puede_votar = utils.puede_votar(votacion_id, user_id)
                # puede_votar = utils.puede_votar(23, user_id) # NO FUNCIONA CORRECTAMENTE SU API
                puede_votar = utils.puede_participar(user_id, votacion_id)

                if not puede_votar and not modificar_voto and not eliminar_voto:
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    modificar_button = types.InlineKeyboardButton("Modificar", callback_data="ID%iM" % votacion_id)
                    eliminar_button = types.InlineKeyboardButton("Eliminar", callback_data="ID%iE" % votacion_id)
                    cancelar_button = types.InlineKeyboardButton("Cancelar", callback_data="CANCEL")
                    markup.add(modificar_button, eliminar_button, cancelar_button)
                    bot.send_message(user_id, 'Ya has participado en esta votación', reply_markup=markup)
                else:
                    votacion = Votacion()
                    votacion.modificar_voto = modificar_voto
                    votacion.get_votacion_api(votacion_id)

                    if self.estado_votacion(votacion) == 'Abierta':
                        variables.sesion[user_id] = votacion
                        if eliminar_voto:
                            votacion.eliminar_votos_api(call)
                            utils.eliminar_participacion(user_id, votacion_id)
                        else:
                            utils.usuario_participa(user_id, votacion_id)
                            votacion.enviar_pregunta(user_id)
                    elif call.id != 1:
                        bot.answer_callback_query(call.id, 'No puedes votar en una votación cerrada')
            else:
                text = 'Debes iniciar sesión para votar, recuerda que puedes hacerlo con el comando /login'
                bot.send_message(user_id, text)

        except Exception as e:
            print(e)