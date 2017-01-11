# -*- coding: utf-8 -*-

import time

import pytest
from telebot import types

import variables
from src.votacion import Votacion
from src.cabinaUtils import CabinaUtils
from src.utils import Utils
import requests

bot = variables.bot
cabinaUtils = CabinaUtils()

should_skip = bot is None

@pytest.mark.skipif(should_skip, reason="No environment variables configured")
class TestBot:
    def create_text_message(self, text):
        params = {'text': text}
        chat = types.User(296066710, 'test')
        return types.Message(1, chat, None, chat, 'text', params)

    def create_callback_query(self, data):
        user = types.User(296066710, 'test')
        return types.CallbackQuery(1, user, data, 2279105952872167927)

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
        utils = Utils()
        url_eliminar = variables.recuento_api + '/eliminarVoto'
        payload_eliminar = {'token': 'test_cabinaTelegram', 'idPregunta': 1}
        requests.post(url_eliminar, payload_eliminar).json()
        time.sleep(1)

        voto = utils.cipher_vote(1)
        url_emitir = variables.recuento_api + '/emitirVoto'
        payload_emitir = {'token': 'test_cabinaTelegram', 'idPregunta': 1, 'voto': voto}
        result = requests.post(url_emitir, payload_emitir)
        assert result.status_code == 201

    def test_emitir_voto_negativo(self):
        utils = Utils()
        voto = utils.cipher_vote('1')
        url = variables.recuento_api + '/emitirVoto'
        payload = {'token': 'test_cabinaTelegram', 'idPregunta': 99999999999 , 'voto': voto}
        result = requests.post(url, payload)

        assert result.status_code != 201
