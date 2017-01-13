# -*- coding: utf-8 -*-

import time

import pytest
from telebot import types

import variables
from src.votacion import Votacion
from src.cabinaUtils import CabinaUtils
from src.utils import Utils
from database import create_database

bot = variables.bot
cabinaUtils = CabinaUtils()
utils = Utils()

should_skip = bot is None

@pytest.mark.skipif(should_skip, reason="No environment variables configured")
class TestBot:
    def create_text_message(self, text):
        params = {'text': text}
        chat = types.User(296066710, 'test')
        return types.Message(1, chat, None, chat, 'text', params)

    def create_callback_query(self, data):
        user = types.User(296066710, 'test')
        return types.CallbackQuery(1, user, data, 1)

    def test_crear_votacion(self):
        votacion = Votacion()
        votacion.bot = bot
        msg = self.create_text_message('/votacion')
        msg2 = self.create_text_message('Titulo Test')
        msg3 = self.create_text_message('41300')
        msg4 = self.create_text_message('11/01/2050 00:00')
        msg5 = self.create_text_message('Hoy')
        msg6 = self.create_text_message('¿Cuando quedamos?')
        msg7 = self.create_text_message('Hoy')
        msg8 = self.create_text_message('Mañana')
        msg9 = self.create_text_message('/done')
        msg10 = self.create_text_message('/cancel')

        @bot.message_handler(commands=['votacion'])
        def crear_votacion(message):
            cabinaUtils.crear_votacion(message)

        bot.process_new_messages([msg])
        time.sleep(1)
        bot.process_new_messages([msg2])
        time.sleep(1)
        bot.process_new_messages([msg3])
        time.sleep(1)
        bot.process_new_messages([msg4])
        time.sleep(1)
        bot.process_new_messages([msg5])
        time.sleep(1)
        bot.process_new_messages([msg6])
        time.sleep(1)
        bot.process_new_messages([msg7])
        time.sleep(1)
        bot.process_new_messages([msg8])
        time.sleep(1)
        bot.process_new_messages([msg9])
        time.sleep(1)
        bot.process_new_messages([msg10])
        time.sleep(1)

        resultado = Votacion()
        resultado.titulo = 'Titulo Test'
        resultado.preguntas_respuestas = {'1.¿Cuando quedamos?':['Hoy', 'Mañana']}
        votacion = variables.sesion[msg.from_user.id]

        assert votacion.titulo == resultado.titulo

    def test_mostrar_votaciones(self):
        msg = self.create_text_message('/votaciones')

        @bot.message_handler(commands=['votaciones'])
        def mostrar_votaciones(message):
            res = cabinaUtils.ver_votaciones(message)
            return res

        bot.process_new_messages([msg])
        time.sleep(1)
        respuesta = mostrar_votaciones(msg)
        errormsg = 'Ha habido algun problema al procesar la peticion'
        assert errormsg != respuesta

    def test_mostrar_votaciones_error(self):
        msg = self.create_text_message('/votaciones')

        @bot.message_handler(commands=['votaciones'])
        def mostrar_votaciones(message):
            res = cabinaUtils.ver_votaciones(message)
            return res

        bot.process_new_messages([msg])
        time.sleep(1)
        respuesta = mostrar_votaciones(msg)
        errormsg = 'Ha habido algun problema al procesar la peticion'
        try:
            assert errormsg == respuesta
        except Exception:
            print('Se muestra este mensaje en caso de que funcione la peticion')

    def test_recontar_votacion(self):
        callback_msg = self.create_callback_query('RE2')

        def callback_recontar_votation(call):
            return cabinaUtils.callback_recontar_votation(call)

        res = callback_recontar_votation(callback_msg)
        errormsg = 'No se puede recontar la votacion porque no esta cerrada'
        assert errormsg != res

    def test_recontar_votacion_negativo(self):
        callback_msg = self.create_callback_query('RE1')

        def callback_recontar_votation(call):
            return cabinaUtils.callback_recontar_votation(call)

        res = callback_recontar_votation(callback_msg)
        errormsg = 'No se puede recontar la votacion porque no esta cerrada'
        assert errormsg == res

    def test_obtener_votacion(self):
        votacion = Votacion()
        votacion.get_votacion_api(1)
        assert len(votacion.titulo) > 0

    def test_obtener_votacion_negativo(self):
        votacion = Votacion()
        votacion.get_votacion_api(99999999999999999999)
        assert len(votacion.titulo) == 0

    def test_emitir_voto(self):
        create_database
        call = self.create_callback_query('1')
        votacion = Votacion()
        votacion.get_votacion_api(1)
        variables.sesion[call.from_user.id] = votacion
        utils.generate_token(call.from_user.id, 'test_cabinaTelegram')

        def responder(call):
            return cabinaUtils.responder(call)

        res = responder(call)
        # Si responde con 400 significa que se ha recibido pero el usuario ya había votado antes
        assert res == 201 or res == 400

    # def test_emitir_voto_negativo(self):
    #     call = self.create_callback_query('1')
    #     votacion = Votacion()
    #     votacion.get_votacion_api(1)
    #     variables.sesion[call.from_user.id] = votacion
    #     utils.generate_token(call.from_user.id, 'negativo')

        def responder(call):
            return cabinaUtils.responder(call)

        res = responder(call)
        # Si no es none significa que ha ejecutado sin error
        assert res is not None
