#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import hashlib
import sqlite3 as lite
import requests
import subprocess
import json
import urllib.request as ur

import variables

class Utils:
    def almacenar_votacion(self,titulo, user_id, preguntas_respuestas):
        # Ruta donde se creará la base de datos (por defecto estará en la carpeta actual)
        path = 'votacion.db'
        #Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
        con = lite.connect(path)
        with con:
            cur = con.cursor()
            #Activar el soporte de sqlite3 para claves foráneas
            cur.execute("""INSERT INTO Votacion(Nombre, Id_Usuario) VALUES(?,?)""", (titulo, user_id))
            aux = cur.execute("""SELECT Votacion.id FROM Votacion WHERE Votacion.Nombre == ?""", (titulo,))
            for row in aux:
                votacionId = row[0]
            # Crear preguntas para esa votación
            for pregunta in sorted(preguntas_respuestas):
                cur.execute("""INSERT INTO Pregunta(Texto,Max_respuestas,Id_votacion) VALUES(?,?,?)""",
                            (pregunta, 50, votacionId))
                aux2 = cur.execute("""SELECT Pregunta.id FROM Pregunta WHERE Pregunta.texto == ?""", (pregunta,))
                for row in aux2:
                    preguntaId = row[0]
                # Almacenar respuestas de
                for respuesta in preguntas_respuestas[pregunta]:
                    cur.execute("""INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES(?,?,?)""",
                                (respuesta, 0, preguntaId))

    def usuario_participa(self, telegram_id, votacion_id):
        try:
            path = 'votacion.db'
            # Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                cur.execute("INSERT OR REPLACE INTO Participacion(Id, Telegram_id, Id_votacion) "
                            "VALUES((SELECT Id FROM Participacion WHERE Telegram_id = ?),?, ?)",
                            (telegram_id, telegram_id, votacion_id))
        except Exception as e:
            print(str(e))

    def puede_participar(self, telegram_id, votacion_id):
        try:
            path = 'votacion.db'
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                logged = cur.execute("SELECT count(Telegram_id) FROM Participacion WHERE Telegram_id = ? AND Id_votacion = ?",
                                     (telegram_id, votacion_id)).fetchone()[0]
                return not bool(logged)
        except Exception as e:
            print(str(e))

    def eliminar_participacion(self, telegram_id, votacion_id):
        try:
            path = 'votacion.db'
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                cur.execute("DELETE FROM Participacion WHERE Telegram_id = ? AND Id_votacion = ?",
                                     (telegram_id, votacion_id))
        except Exception as e:
            print(str(e))

    def get_votacion(self, idVotacion):
        # Ruta donde se creará la base de datos (por defecto estará en la carpeta actual)
        path = 'votacion.db'
        # Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
        con = lite.connect(path)
        with con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            votacion = cur.execute("""SELECT Nombre FROM Votacion WHERE Id == ?""", (idVotacion,)).fetchone()[0]
            user_id = cur.execute("""SELECT Id_Usuario FROM Votacion WHERE Id == ?""", (idVotacion,)).fetchone()[0]
            diccionario = {}
            preguntas = cur.execute("""SELECT Texto FROM Pregunta WHERE Id_votacion LIKE ?""", (idVotacion,)).fetchall()
            for row in preguntas:
                aux = cur.execute("""SELECT Id FROM Pregunta WHERE Pregunta.texto LIKE ?""", (row[0],)).fetchone()
                nombrePregunta = row[0]
                idPregunta = aux[0]
                auxRespuestas = cur.execute("""SELECT Texto FROM Respuesta WHERE Respuesta.Id_pregunta == ? group by Texto""",
                                            (idPregunta,)).fetchall()
                respuestas = []
                for row in auxRespuestas:
                    respuestas.append(row[0])

                diccionario[nombrePregunta] = respuestas
        return [votacion, user_id, diccionario, idVotacion]

    def get_votaciones(self, user_id):
        votaciones = []
        try:
            # Ruta donde se creará la base de datos. En sistemas UNIX-like será /home/username/votacion.db
            # Ruta donde se creará la base de datos (por defecto estará en la carpeta actual)
            path = 'votacion.db'
            # Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                id_votaciones = cur.execute("""SELECT Votacion.id FROM Votacion WHERE Votacion.Id_usuario = ?""", (user_id,)).fetchall()
            for id_votacion in id_votaciones:
                votaciones.append(self.get_votacion(id_votacion[0]))
            return votaciones

        except Exception as e:
            print(e)

    def cipher_vote(self, vote):
        try:
            url = 'https://api.github.com/repos/AgoraUS-G1-1617/Recuento-y-modificacion/contents/verification.jar'
            response = requests.get(url)
            jar_file_url = json.loads(response.text)['download_url']
            jar_sha = json.loads(response.text)['sha']
            if jar_sha != variables.jar_sha:
                r = requests.get(jar_file_url)
                with open("src/main/python/src/verification.jar", "wb") as verification:
                    verification.write(r.content)
                variables.jar_sha = jar_sha
        except Exception as e:
            print(str(e))

        try:
            url = 'https://recuento.agoraus1.egc.duckdns.org/api/clavePublica'
            public_key = requests.get(url).text
            ans = subprocess.check_output(['java', '-jar', 'src/main/python/src/verification.jar', 'cipher', '%s' % vote, '%s' % public_key])
        except:
            ans = None
        return ans

    def generate_token(self, telegram_id, auth_token):
        verify_token = hashlib.sha1(os.urandom(128)).hexdigest()
        try:
            path = 'votacion.db' # CAMBIAR
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                cur.execute("INSERT OR REPLACE INTO Usuario(Id, Telegram_id, VerifyToken, AuthToken, Logged) "
                            "VALUES((select Id from Usuario where Telegram_id = ?),?,?,?,?)",
                            (telegram_id, telegram_id, verify_token, auth_token,0))
            return verify_token
        except Exception as e:
            print(str(e))

    def set_logged(self, telegram_id, verify_token):
        try:
            path = 'votacion.db'
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                cur.execute("UPDATE Usuario SET Logged = 1 WHERE Telegram_id = ? AND VerifyToken = ?", (telegram_id, verify_token))
                logged = cur.execute("SELECT Logged FROM Usuario WHERE Telegram_id = ?", (telegram_id,)).fetchone()[0]
                return bool(logged)
        except Exception as e:
            print(str(e))

    def get_logged(self, telegram_id):
        try:
            path = 'votacion.db'
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                logged = cur.execute("SELECT Logged FROM Usuario WHERE Telegram_id = ?", (telegram_id,)).fetchone()[0]
                return bool(logged)
        except Exception as e:
            print(str(e))

    def logout(self, telegram_id):
        try:
            path = 'votacion.db'
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                cur.execute("UPDATE Usuario SET Logged = 0 WHERE Telegram_id = ? ", (telegram_id,))
                logged = cur.execute("SELECT Logged FROM Usuario WHERE Telegram_id = ?", (telegram_id,)).fetchone()[0]
                return bool(logged)
        except Exception as e:
            print(str(e))

    def extract_unique_code(self, text):
        # Extracts the unique_code from the sent /start command.
        return text.split()[1] if len(text.split()) > 1 else None

    def get_auth_token(self, username, password):
        pre_token = username + hashlib.md5(password.encode()).hexdigest()
        token = username + ':' + hashlib.md5(pre_token.encode()).hexdigest()
        return token

    def get_auth_token_telegramId(self, telegram_id):
        try:
            path = 'votacion.db'
            con = lite.connect(path)
            with con:
                cur = con.cursor()
                auth_token = cur.execute("SELECT AuthToken FROM Usuario WHERE Telegram_id = ?", (telegram_id,)).fetchone()[0]
                return auth_token
        except Exception as e:
            print(str(e))

    def check_token(self, token):
        url = 'https://authb.agoraus1.egc.duckdns.org/api/index.php?method=checkToken&token=%s' % token
        response = requests.get(url)
        valid = json.loads(response.text.replace('\ufeff', ''))['valid']
        return valid

    def check_credentials(self, username, password):
        token = self.get_auth_token(username, password)
        return self.check_token(token)

    def obtener_votaciones(self):
        try:
            url = variables.recuento_api + '/verVotaciones'
            html = ur.urlopen(url).read()
            data = json.loads(html.decode('utf-8'))
            diccionario_votaciones = data.get('votaciones')
            return diccionario_votaciones
        except Exception as e:
            print(str(e))