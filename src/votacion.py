# -*- encoding: utf-8 -*-

import telebot
from telebot import types
import requests
import datetime

import variables
from src.utils import Utils

utils = Utils()

bot = variables.bot

class Votacion:
    def __init__(self):
        self.id_votacion = 0
        self.id_primera_pregunta = 0
        self.titulo = ""
        self.fecha_creacion = datetime.datetime.now()
        self.fecha_cierre = datetime.datetime.now()
        self.cp = ""
        self.preguntas_respuestas = {}
        self.respuestas_seleccionadas = []
        self.owner_id = 0
        self.temp_msg_question_id = None
        self.temp_preguntas = None
        self.temp_id_opcion = 0
        self.modificar_voto = False

    def crear_votacion(self, message):
        self.pide_titulo(message.chat.id)
        self.owner_id = message.from_user.id

    def pide_titulo(self, chat_id):
        msg = bot.send_message(chat_id, 'Dime un *título* para la votación:', parse_mode='Markdown')
        bot.register_next_step_handler(msg, self.captura_titulo)

    def captura_titulo(self, message):
        titulo = message.text[:30]
        chat_id = message.chat.id

        if telebot.util.is_command(titulo):
            bot.send_message(message.chat.id, '❌ Votación cancelada')
            return False
        else:
            self.titulo = titulo
            self.pide_cp(chat_id)

    def pide_cp(self, chat_id):
        msg = bot.send_message(chat_id, 'Dime tu *CP* para la votación:', parse_mode='Markdown')
        bot.register_next_step_handler(msg, self.captura_cp)

    def captura_cp(self, message):
        cp = message.text
        chat_id = message.chat.id

        if telebot.util.is_command(cp):
            bot.send_message(message.chat.id, '❌ Votación cancelada')
            return False
        elif cp.isdigit() and len(cp) == 5:
            self.cp = cp
            self.pide_fecha_cierre(chat_id)
        else:
            msg = bot.send_message(message.chat.id, 'Introduzca un CP numérico de longitud 5')
            bot.register_next_step_handler(msg, self.captura_cp)

    def pide_fecha_cierre(self, chat_id):
        msg = bot.send_message(chat_id, 'Dime una *fecha de cierre* con el formato "dd/mm/YYYY HH:MM":', parse_mode='Markdown')
        bot.register_next_step_handler(msg, self.captura_fecha_cierre)

    def captura_fecha_cierre(self, message):
        fecha_cierre = message.text
        chat_id = message.chat.id
        now = datetime.datetime.now()

        if telebot.util.is_command(fecha_cierre):
            bot.send_message(message.chat.id, '❌ Votación cancelada')
            return False
        else:
            try:
                fecha_cierre = datetime.datetime.strptime(fecha_cierre, '%d/%m/%Y %H:%M')
                assert fecha_cierre > now
                self.fecha_cierre = fecha_cierre
                self.pide_pregunta(chat_id)
            except:
                msg = bot.send_message(message.chat.id, 'Introduzca una fecha futura correcta (dd/mm/YYYY HH:MM)')
                bot.register_next_step_handler(msg, self.captura_fecha_cierre)

    def pide_pregunta(self, chat_id):
        if self.get_num_preguntas() == 0:
            text = '❔Dime tu primera *pregunta:*'
        else:
            text = '❔Siguiente *pregunta:* \n\nPara terminar escribe /done o simplemente pulsa sobre el enlace.'
        msg = bot.send_message(chat_id, text, parse_mode='Markdown')
        bot.register_next_step_handler(msg, self.captura_pregunta)

    def captura_pregunta(self, message):
        pregunta = message.text[:128]
        chat_id = message.chat.id

        if telebot.util.is_command(pregunta):
            command = telebot.util.extract_command(pregunta)
            if command == 'done' and self.get_num_preguntas() >= 1:
                utils.almacenar_votacion(self.titulo, self.owner_id, self.preguntas_respuestas)
                self.put_votacion_api()
                bot.send_message(chat_id, '✅ Encuesta creada con éxito')
                bot.send_message(chat_id, str(self.to_string()), parse_mode='Markdown')
            elif command == 'done':
                bot.send_message(chat_id, 'Necesitas al menos una pregunta para crear la votación.')
                self.pide_pregunta(chat_id)
            else:
                bot.send_message(chat_id, '❌ Votación cancelada')
                return False
        else:
            self.añade_pregunta(pregunta)
            self.pide_respuesta(message.chat.id)

    def pide_respuesta(self, chat_id):
        if self.get_num_respuestas() == 0:
            text = '✏️ Dime una *respuesta:*'
        elif self.get_num_respuestas() == 1:
            text = '✏️ Dime otra *respuesta:*'
        else:
            text = '✏️ Dime otra *respuesta:* \n\nPara pasar a la siguiente pregunta escribe /done' \
                   ' o simplemente pulsa sobre el enlace.'

        msg = bot.send_message(chat_id, text, parse_mode='Markdown')
        bot.register_next_step_handler(msg, self.captura_respuesta)

    def captura_respuesta(self, message):
        respuesta = message.text[:128]
        chat_id = message.chat.id

        if telebot.util.is_command(respuesta):
            command = telebot.util.extract_command(respuesta)
            if command == 'done' and self.get_num_respuestas() >= 2:
                self.pide_pregunta(chat_id)
            elif command == 'done':
                bot.send_message(chat_id, 'Necesitas al menos dos respuestas para la pregunta.')
                self.pide_respuesta(chat_id)
            else:
                bot.send_message(chat_id, '❌ Votación cancelada')
                return False
        else:
            self.añade_respuesta(respuesta)
            self.pide_respuesta(chat_id)

    def mostrar_preguntas(self):
        return sorted(self.preguntas_respuestas)

    def mostrar_respuestas(self, pregunta):
        return self.preguntas_respuestas[pregunta]

    def añade_pregunta(self, pregunta):
        num_preguntas = len(self.preguntas_respuestas)
        self.preguntas_respuestas['%d. %s' % (num_preguntas+1, pregunta)] = []

    def añade_respuesta(self, respuesta):
        pregunta = sorted(self.preguntas_respuestas)[-1]
        self.preguntas_respuestas[pregunta].append(respuesta[:128])

    def get_num_preguntas(self):
        return len(self.preguntas_respuestas)

    def get_num_respuestas(self):
        pregunta = sorted(self.preguntas_respuestas)[-1]
        return len(self.preguntas_respuestas[pregunta])

    def enviar_pregunta(self, chat_id):
        if self.temp_preguntas is None:
            self.temp_preguntas = self.mostrar_preguntas()
            self.temp_preguntas.reverse()
        if len(self.temp_preguntas) == 0:
            bot.edit_message_text('👍 Gracias por su participación', chat_id=chat_id,
                                  message_id=self.temp_msg_question_id)
            self.temp_msg_question_id = None
            self.temp_preguntas = None
            return False
        pregunta = self.temp_preguntas.pop()
        respuestas = self.mostrar_respuestas(pregunta)
        pregunta_txt = '*%s*\n\n%i. %s' % (self.titulo, len(self.respuestas_seleccionadas)+1, pregunta)
        markup = types.InlineKeyboardMarkup()
        for respuesta in respuestas:
            markup.add(types.InlineKeyboardButton(respuesta[:128], callback_data=str(self.temp_id_opcion)))
            self.temp_id_opcion += 1
        if self.temp_msg_question_id is None:
            msg_question = bot.send_message(chat_id, pregunta_txt, reply_markup=markup, parse_mode='Markdown')
            self.temp_msg_question_id = msg_question.message_id
        else:
            bot.edit_message_text(pregunta_txt, chat_id=chat_id, message_id=self.temp_msg_question_id, parse_mode='Markdown')
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=self.temp_msg_question_id, reply_markup=markup)

    def responder_pregunta(self, call):
        respuesta = call.data
        chat_id = call.from_user.id
        id_pregunta = self.id_primera_pregunta + len(self.respuestas_seleccionadas)
        try:
            voto = utils.cipher_vote(respuesta)
            if self.modificar_voto:
                url = variables.recuento_api + '/modificarVoto'
                payload = {'token': utils.get_auth_token_telegramId(chat_id), 'idPregunta': id_pregunta, 'nuevoVoto': voto}
            else:
                url = variables.recuento_api + '/emitirVoto'
                payload = {'token': utils.get_auth_token_telegramId(chat_id), 'idPregunta': id_pregunta, 'voto': voto}
            result = requests.post(url, payload)
            if result.status_code == 502 and call.id != 1:
                bot.answer_callback_query(call.id, 'Operación no permitida')
            elif call.id != 1:
                result = result.json()
                bot.answer_callback_query(call.id, result['mensaje'])
            else:
                return result.status_code
        except Exception as e:
            bot.send_message(chat_id, str(e))
        self.respuestas_seleccionadas.append(respuesta)
        self.enviar_pregunta(chat_id)

    def to_string(self):
        text = '*%s*\n\n' % self.titulo
        for pregunta in sorted(self.preguntas_respuestas):
            text += '%s\n' % pregunta
            for respuesta in self.preguntas_respuestas[pregunta]:
                text += '    ▫️ %s\n' % respuesta

        return text

    def get_votacion_api(self, idVotacion):
        try:
            url = variables.recuento_api + '/verVotacion?idVotacion=%i&detallado=si' % idVotacion
            json = requests.get(url).json()
            self.titulo = json['votacion']['titulo']
            self.cp = json['votacion']['cp']
            fecha_creacion = json['votacion']['fecha_creacion']
            self.fecha_creacion = datetime.datetime.strptime(fecha_creacion, '%Y-%m-%d %H:%M:%S')
            fecha_cierre = json['votacion']['fecha_cierre']
            self.fecha_cierre = datetime.datetime.strptime(fecha_cierre, '%Y-%m-%d %H:%M:%S')
            preguntas = json['votacion']['preguntas']
            for p in preguntas:
                if preguntas.index(p) == 0:
                    self.id_primera_pregunta = int(p['id_pregunta'])
                    self.temp_id_opcion = int(p['opciones'][0]['id_opcion'])
                pregunta = p['texto_pregunta']
                respuestas = []
                for r in p['opciones']:
                    respuestas.append(r['texto_opcion'])
                self.preguntas_respuestas[pregunta] = respuestas
        except Exception as e:
            print(str(e))
            return 'No se puede obtener la votación. Vuelva a intentarlo mas tarde...'

    def put_votacion_api(self):
        try:
            url = variables.recuento_api + '/crearVotacion'
            preguntas_to_api = []
            preguntas = self.mostrar_preguntas()
            for pregunta in preguntas:
                respuestas = self.mostrar_respuestas(pregunta)
                pregunta_to_api = {"texto_pregunta": pregunta.split('. ')[1],
                                   "multirespuesta": False,
                                   "opciones": respuestas}
                preguntas_to_api.append(pregunta_to_api)

            json = {"titulo": self.titulo,
                       "cp": self.cp,
                       "fecha_cierre": str(self.fecha_cierre),
                       "preguntas": preguntas_to_api}
            result = requests.post(url, json=json)
            print(result.text)
        except Exception as e:
            print(str(e))

    def eliminar_votos_api(self, call):
        result = {'mensaje': '...'}
        user_id = call.from_user.id
        try:
            url = variables.recuento_api + '/eliminarVoto'
            id_ultima_pregunta = self.id_primera_pregunta + len(self.mostrar_preguntas())
            for id_pregunta in range(self.id_primera_pregunta, id_ultima_pregunta):
                payload = {'token': utils.get_auth_token_telegramId(user_id), 'idPregunta': id_pregunta}
                result = requests.post(url, payload).json()
                print(result)
            if call.id != 1:
                bot.answer_callback_query(call.id, result['mensaje'])
        except Exception as e:
            print(str(e))

class Panel:

    def query_text(self, inline_query):
        try:
            diccionario_votaciones = utils.obtener_votaciones()
            res = []
            for votacion in diccionario_votaciones:
                titulo = votacion['titulo']
                votacion_id = votacion['id_votacion']
                if inline_query.query.lower() in titulo.lower() or inline_query.query == str(votacion_id):
                    text = 'Has sido invitado para participar en la votación:️\n✉️ %s\n\n' \
                           'Recuerda iniciar el bot si todavía no lo has hecho.' % titulo
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Comenzar votación', callback_data='ID%s' % str(votacion_id)))
                    r = types.InlineQueryResultArticle(str(votacion_id), titulo, types.InputTextMessageContent(text),
                                                       reply_markup=markup)
                    res.append(r)

            bot.answer_inline_query(inline_query.id, res)
        except Exception as exception:
            print(str(exception))