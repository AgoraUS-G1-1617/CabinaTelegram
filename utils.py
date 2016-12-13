#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3 as lite

class Utils:
    def almacenar_votacion(self,titulo, user_id, preguntas_respuestas):
        #Ruta donde se creará la base de datos. En sistemas UNIX-like será /home/username/votacion.db
        home = os.path.expanduser('~')
        path = home + '/votacion.db'
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
            for pregunta in preguntas_respuestas:
                cur.execute("""INSERT INTO Pregunta(Texto,Max_respuestas,Id_votacion) VALUES(?,?,?)""",
                            (pregunta, 50, votacionId))
                aux2 = cur.execute("""SELECT Pregunta.id FROM Pregunta WHERE Pregunta.texto == ?""", (pregunta,))
                for row in aux2:
                    preguntaId = row[0]
                # Almacenar respuestas de
                for respuesta in preguntas_respuestas[pregunta]:
                    cur.execute("""INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES(?,?,?)""",
                                (respuesta, 0, preguntaId))

    def get_votacion(self, idVotacion):
        # Ruta donde se creará la base de datos. En sistemas UNIX-like será /home/username/votacion.db
        home = os.path.expanduser('~')
        path = home + '/votacion.db'
        # Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
        con = lite.connect(path)
        with con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            votacion = cur.execute("""SELECT Nombre FROM Votacion WHERE Id == ?""", (idVotacion,))
            diccionario = {}
            preguntas = cur.execute("""SELECT Texto FROM Pregunta WHERE Id_votacion LIKE ?""", (idVotacion,))
            for row in preguntas:
                aux = cur.execute("""SELECT Id FROM Pregunta WHERE Pregunta.texto LIKE ?""", (row[0],))
                nombrePregunta = row[0]
                idPregunta = 0
                for x in aux:
                    idPregunta = x[0]
                auxRespuestas = cur.execute("""SELECT Texto FROM Respuesta WHERE Respuesta.Id_pregunta LIKE ?""",
                                            (idPregunta,))
                respuestas = []
                for row in auxRespuestas:
                    respuestas.append(row[0])

            diccionario[nombrePregunta] = respuestas
        return [votacion, diccionario]
