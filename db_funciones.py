#!/usr/bin/python
"""db_functions.py: Funciones para la interacción con la base de datos"""
__author__ = "Ana María Manso Rodríguez"
__credits__ = ["Ana María Manso Rodríguez"]
__version__ = "1.0"
__status__ = "Development"

from datetime import datetime
import sys

import mariadb
import pandas as pd

from config import config


# Function to connect to db
def connect_ddbb():
    try:
        params = config()
        myconnection = mariadb.connect(**params)
        return myconnection
    except (Exception, mariadb.DatabaseError) as error:
        print(error)


# Function that gets record dates from db
def get_record_dates(date=False):
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    # If date is provided, get record dates from that date in db
    if date:
        sql = "SELECT id_event, description, date_time FROM record_dates WHERE date_time >= %s"
        mycursor.execute(sql, [str(date)])
    # If date is not provided, gets all record dates in db
    else:
        sql = "SELECT id_event, description, date_time FROM record_dates"
        mycursor.execute(sql)

    data = mycursor.fetchall()
    close_connection_to_db(conexion)
    values = []
    for i in range(len(data)):
        values.append(str(data[i][0]) + '···' + data[i][1] + '···' + str(data[i][2]))
    return values


# Function that inserts student data and nfc_tag in db
def insert_student_to_db(datos, tag_uid):
    conexion = connect_ddbb()
    registro = [datos[0], datos[1], datos[2], tag_uid]
    mycursor = conexion.cursor()
    sql = "INSERT INTO students (student_id, student_name, student_last_name, nfc_uid) VALUES (%s,%s,%s,%s)"
    print(registro)
    mycursor.execute(sql, registro)
    conexion.commit()
    close_connection_to_db(conexion)


# Function that returns students data from db
def get_student_from_db(id_m):
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    sql = "SELECT student_name,student_last_name FROM students WHERE student_id = %s"
    mycursor.execute(sql, [id_m])
    student = mycursor.fetchall()
    close_connection_to_db(conexion)
    return student[0]


# Funtion that returns students without a NFC tag associated
def get_students_from_db():
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    sql = "SELECT * FROM students WHERE nfc_uid IS NULL"
    mycursor.execute(sql)
    students = mycursor.fetchall()
    close_connection_to_db(conexion)
    return students


# Function that insert NFC uid in DB
def set_student_nfc_true(student, num):
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    sql = "UPDATE students SET nfc_uid = %s WHERE student_id = %s"
    val = (num, student[0])
    mycursor.execute(sql, val)
    conexion.commit()
    close_connection_to_db(conexion)


# Function that inserts student record in db
def insert_student_record(examn, student, name, last_name):
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    now = datetime.now()
    val = [examn, student, name, last_name, now]
    sql = "INSERT INTO students_attendance (id_event, student_id, student_name, student_last_name, datetime) values (%s,%s,%s,%s,%s)"
    mycursor.execute(sql, val)
    conexion.commit()
    close_connection_to_db(conexion)


# Function that return description in db
def get_description(id_event):
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    sql = "SELECT description FROM record_dates WHERE id_event = %s"
    mycursor.execute(sql, [id_event])
    desc = mycursor.fetchone()
    return desc[0]


# Function that return email in db
def get_email(id_event):
    conexion = connect_ddbb()
    mycursor = conexion.cursor()
    sql = "SELECT email FROM record_dates WHERE id_event = %s"
    mycursor.execute(sql, [id_event])
    email = mycursor.fetchone()
    return email[0]


# Function that return dataframe with students record results
def get_students_records(id_e):
    conexion = connect_ddbb()
    # Query, students to record attendance
    sql1 = '''SELECT a.student_id, b.student_name, b.student_last_name
    FROM registration a, students b
    WHERE (a.id_group,a.subject) in (select id_group,subject from examn_groups where id_event = (%s))
    and a.student_id = b.student_id'''
    df1 = pd.read_sql_query(sql1, con=conexion, params=(id_e, id_e))
    # Query, students attendance recorded
    sql2 = '''SELECT * FROM students_attendance WHERE id_event = (%s)'''
    df2 = pd.read_sql_query(sql2, con=conexion, params=(id_e,))
    # Merge dataframes
    df3 = pd.merge(df1, df2, on=['student_id', 'student_name', 'student_last_name'], how='left')
    return df3


# Function that close db conection
def close_connection_to_db(conexion):
    conexion.close()
