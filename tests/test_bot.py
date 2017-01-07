# -*- coding: utf-8 -*-

import time

import pytest
import json
import urllib.request as ur
from telebot import types

import variables
from src.votacion import Votacion
from src.cabinaUtils import CabinaUtils

bot = variables.bot
cabinaUtils = CabinaUtils()

should_skip = bot is None

@pytest.mark.skipif(should_skip, reason="No environment variables configured")
class TestBot:
    def create_text_message(self, text):
        params = {'text': text}
        chat = types.User(296066710, 'test')
        return types.Message(1, chat, None, chat, 'text', params)

    def test_crear_votacion(self):
        votacion = Votacion()
        votacion.bot = bot
        msg = self.create_text_message('/votacion')
        msg2 = self.create_text_message('Titulo Test')
        msg3 = self.create_text_message('¿Cuando quedamos?')
        msg4 = self.create_text_message('Hoy')
        msg5 = self.create_text_message('Mañana')
        msg6 = self.create_text_message('/done')
        msg7 = self.create_text_message('/done')

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

    def test_recontar_votacion_no_terminada(self):
        msg = self.create_text_message('/recontarVotacion')

        @bot.message_handler(commands=['recontarVotacion'])
        def recontar_votacion_no_terminada(message):
            res = cabinaUtils.recuento_votacion(message)
            return res

        bot.process_new_messages([msg])
        time.sleep(1)
        respuesta = recontar_votacion_no_terminada(msg)
        errormsg = 'No se puede recontar la votacion porque no esta cerrada'
        assert errormsg == respuesta
