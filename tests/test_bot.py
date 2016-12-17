# -*- coding: utf-8 -*-

import time

import pytest
from telebot import types

import variables
from src.votacion import Votacion

bot = variables.bot

should_skip = bot is None

@pytest.mark.skipif(should_skip, reason="No environment variables configured")
class TestBot:
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
            user_id = message.from_user.id
            votacion.crear_votacion(message)
            variables.sesion[user_id] = votacion

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

        assert votacion.titulo == resultado.titulo

    def create_text_message(self, text):
        params = {'text': text}
        chat = types.User(296066710, 'test')
        return types.Message(1, chat, None, chat, 'text', params)
