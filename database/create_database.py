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

    #Borrar las tablas existentes
    # cur.execute("DROP TABLE IF EXISTS Participacion")
    # cur.execute("DROP TABLE IF EXISTS Respuesta")
    # cur.execute("DROP TABLE IF EXISTS Pregunta")
    # cur.execute("DROP TABLE IF EXISTS Votacion")
    # cur.execute("DROP TABLE IF EXISTS Usuario")

    #Crear tabla de Usuario
    cur.execute("CREATE TABLE IF NOT EXISTS Usuario(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Telegram_id INTEGER, VerifyToken TEXT, AuthToken TEXT, Logged INTEGER)")      #Aquí habrá que poner que la Telegram_id no puede ser nula

    #Crear tabla de Votacion
    cur.execute("CREATE TABLE IF NOT EXISTS Votacion(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Nombre TEXT NOT NULL,Id_Usuario INTEGER NOT NULL,FOREIGN KEY (Id_Usuario) REFERENCES Usuario(Id))")

    #Crear tabla de Participación
    # cur.execute("CREATE TABLE IF NOT EXISTS Participacion(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Id_usuario INTEGER NOT NULL,Id_votacion INTEGER NOT NULL, FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id), FOREIGN KEY (Id_votacion) REFERENCES Votacion(Id))")
    cur.execute("CREATE TABLE IF NOT EXISTS Participacion(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Telegram_id INTEGER NOT NULL,Id_votacion INTEGER NOT NULL)")

    #Crear tabla de Pregunta
    cur.execute("CREATE TABLE IF NOT EXISTS Pregunta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Texto TEXT NOT NULL,Max_respuestas INT NOT NULL DEFAULT 1,Id_votacion INTEGER NOT NULL, FOREIGN KEY (Id_votacion) REFERENCES Votacion(Id))")

    #Crear tabla de Respuesta
    cur.execute("CREATE TABLE IF NOT EXISTS Respuesta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Texto TEXT NOT NULL,Veces_elegida INT NOT NULL DEFAULT 0,Id_pregunta INTEGER NOT NULL, FOREIGN KEY (Id_pregunta) REFERENCES Pregunta(Id))")