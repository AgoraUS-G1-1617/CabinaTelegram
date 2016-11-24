#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3 as lite
import sys



#Ruta donde se creará la base de datos. En sistemas UNIX-like será /home/username/votacion.db
home = os.path.expanduser('~')
path = home + '/votacion.db'

#Crea una conexión con la base de datos establecida en la ruta. Si no existe la base de datos, se creará una nueva
con = lite.connect(path)

with con:

    cur = con.cursor()

    #Activar el soporte de sqlite3 para claves foráneas
    cur.execute("PRAGMA foreign_keys = ON")

    #Borrar las tablas existentes
    cur.execute("DROP TABLE IF EXISTS Participacion")
    cur.execute("DROP TABLE IF EXISTS Usuario")
    cur.execute("DROP TABLE IF EXISTS Respuesta")
    cur.execute("DROP TABLE IF EXISTS Pregunta")
    cur.execute("DROP TABLE IF EXISTS Encuesta")

    #Crear tabla de Usuario
    cur.execute("CREATE TABLE Usuario(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Telegram_id INTEGER)")      #Aquí habrá que poner que la Telegram_id no puede ser nula

    #Crear tabla de Encuesta
    cur.execute("CREATE TABLE Encuesta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Nombre TEXT NOT NULL)")

    #Crear tabla de Participación
    cur.execute("CREATE TABLE Participacion(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Id_usuario INTEGER NOT NULL,Id_encuesta INTEGER NOT NULL, FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id), FOREIGN KEY (Id_encuesta) REFERENCES Encuesta(Id))")


    #Crear tabla de Pregunta
    cur.execute("CREATE TABLE Pregunta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Texto TEXT NOT NULL,Max_respuestas INT NOT NULL DEFAULT 1,Id_encuesta INTEGER NOT NULL, FOREIGN KEY (Id_encuesta) REFERENCES Encuesta(Id))")

    #Crear tabla de Respuesta
    cur.execute("CREATE TABLE Respuesta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Texto TEXT NOT NULL,Veces_elegida INT NOT NULL DEFAULT 0,Id_pregunta INTEGER NOT NULL, FOREIGN KEY (Id_pregunta) REFERENCES Pregunta(Id))")