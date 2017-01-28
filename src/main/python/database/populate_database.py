#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3 as lite

#Ruta donde se creará la base de datos (por defecto estará en la carpeta actual)
path = 'votacion.db'

#Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
con = lite.connect(path)

with con:

    cur = con.cursor()

    #Activar el soporte de sqlite3 para claves foráneas
    cur.execute("PRAGMA foreign_keys = ON")

    #Insertar datos en la tabla de Usario
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(220)")
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(230)")
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(240)")
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(250)")

    #Insertar datos en la tabla de Votacion
    cur.execute("INSERT INTO Votacion(Nombre,Id_Usuario) VALUES('Votacion1',1)")
    cur.execute("INSERT INTO Votacion(Nombre,Id_Usuario) VALUES('Votacion2',1)")
    cur.execute("INSERT INTO Votacion(Nombre,Id_Usuario) VALUES('Votacion3',2)")
    cur.execute("INSERT INTO Votacion(Nombre,Id_Usuario) VALUES('Votacion4',2)")

    #Insertar datos en la tabla de Participación
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_votacion) VALUES(2,1)")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_votacion) VALUES(2,1)")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_votacion) VALUES(3,2)")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_votacion) VALUES(3,3)")


    #Insertar datos en la tabla dePregunta
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_votacion) VALUES('¿Qué hora es?',2,1)")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_votacion) VALUES('¿Cuántos años tienes?',4,2)")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_votacion) VALUES('¿Te gusta el yogur de fresa?',6,3)")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_votacion) VALUES('¿Si o que?',8,4)")

    #Insertar datos en la tabla de Respuesta
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('Las 12',5,1)")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('Más de 50',6,2)")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('Sí',7,3)")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('¿que?',8,1)")