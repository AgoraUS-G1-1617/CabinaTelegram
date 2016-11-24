#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sqlite3 as lite
import sys



#Ruta donde se creará la base de datos. En sistemas UNIX-like será /home/username/encuestas.db
home = os.path.expanduser('~')
path = home + '/encuestas.db'

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
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(220)")
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(230)")
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(240)")
    cur.execute("INSERT INTO Usuario(Telegram_id) VALUES(250)")

    #Crear tabla de Encuesta
    cur.execute("CREATE TABLE Encuesta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Nombre TEXT NOT NULL)")
    cur.execute("INSERT INTO Encuesta(Nombre) VALUES('Encuesta1')")
    cur.execute("INSERT INTO Encuesta(Nombre) VALUES('Encuesta2')")
    cur.execute("INSERT INTO Encuesta(Nombre) VALUES('Encuesta3')")
    cur.execute("INSERT INTO Encuesta(Nombre) VALUES('Encuesta4')")

    #Crear tabla de Participación
    cur.execute("CREATE TABLE Participacion(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Id_usuario INTEGER NOT NULL,Id_encuesta INTEGER NOT NULL, FOREIGN KEY (Id_usuario) REFERENCES Usuario(Id), FOREIGN KEY (Id_encuesta) REFERENCES Encuesta(Id))")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_encuesta) VALUES(2,1)")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_encuesta) VALUES(2,1)")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_encuesta) VALUES(3,2)")
    cur.execute("INSERT INTO Participacion(Id_usuario,Id_encuesta) VALUES(3,3)")


    #Crear tabla de Pregunta
    cur.execute("CREATE TABLE Pregunta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Texto TEXT NOT NULL,Max_respuestas INT NOT NULL DEFAULT 1,Id_encuesta INTEGER NOT NULL, FOREIGN KEY (Id_encuesta) REFERENCES Encuesta(Id))")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_encuesta) VALUES('¿Qué hora es?',2,1)")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_encuesta) VALUES('¿Cuántos años tienes?',4,2)")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_encuesta) VALUES('¿Te gusta el yogur de fresa?',6,3)")
    cur.execute("INSERT INTO Pregunta(Texto,Max_respuestas,Id_encuesta) VALUES('¿Si o que?',8,4)")

    #Crear tabla de Respuesta
    cur.execute("CREATE TABLE Respuesta(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,Texto TEXT NOT NULL,Veces_elegida INT NOT NULL DEFAULT 0,Id_pregunta INTEGER NOT NULL, FOREIGN KEY (Id_pregunta) REFERENCES Pregunta(Id))")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('Las 12',5,1)")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('Más de 50',6,2)")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('Sí',7,3)")
    cur.execute("INSERT INTO Respuesta(Texto,Veces_elegida,Id_pregunta) VALUES('¿que?',8,1)")