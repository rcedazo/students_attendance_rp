#!/usr/bin/python
"""app.py: Interfaz grafica para el registro de los estudiante y la interaccion
con los NFC tags del sistema de registro de asistencia"""
__author__ = "Ana María Manso Rodríguez"
__credits__ = ["Ana María Manso Rodríguez"]
__version__ = "1.0"
__status__ = "Development"

import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

from datetime import date
from datetime import timedelta
import mariadb
import pandas as pd
from PIL import Image, ImageTk

import NFC_tag
from db_funciones import *
from widget_aux import *
from mail_function import *


# Pagina principal
class MainMenu:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.image = Image.open('Captura.jpg')
        self.image = self.image.resize((271, 129))
        self.image = ImageTk.PhotoImage(self.image)

        self.logo = tk.Label(self.frame, image=self.image)
        self.logo.grid(row=0, column=0, pady=20)

        # -----------Buttons-----------

        # Init recording button
        self.buttonInitRecording = tk.Button(self.frame, text='Iniciar examen', height=1, width=25, bg="SteelBlue1",
                                             fg="white", command=self.openInitRecording)
        self.buttonInitRecording.grid(row=1, column=0, pady=4)

        # Get Records button
        self.buttonGetRecord = tk.Button(self.frame, text='Registros', height=1, width=25, bg="SteelBlue1", fg="white",
                                         command=self.openGetRecords)
        self.buttonGetRecord.grid(row=2, column=0, pady=4)

        # Students Administration
        self.buttonStudentsAdmin = tk.Button(self.frame, text="Gestión alumnos", height=1, width=25, bg="SteelBlue1",
                                             fg="white", command=self.openStudentsAdmin)
        self.buttonStudentsAdmin.grid(row=3, column=0, pady=4)

        self.frame.pack(expand=True)
        self.frame.config(bg="white")

    # Open Init Recording window
    def openInitRecording(self):
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.title("ETSIDI Asistencia - Iniciar examen")
        self.newWindow.config(bg="white")
        self.app = InitRecording(self.newWindow)

    # Open Get Records window
    def openGetRecords(self):
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.title("ETSIDI Asistencia - Registros")
        self.app = GetRecords(self.newWindow)

    # Open Students Administration window
    def openStudentsAdmin(self):
        self.newWindow = tk.Toplevel(self.master)
        self.newWindow.title("ETSIDI Asistencia - Gestión estudiantes")
        self.newWindow.config(bg="white")
        self.app = StudentsAdmin(self.newWindow)


# Ventana de aplicacion
class GetRecords:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.pw = tk.StringVar()

        values = get_record_dates()

        # -----------Labels------------

        self.passwordLabel = tk.Label(self.frame, text="Contraseña para el envío de resultados :")
        self.passwordLabel.grid(row=2, column=0, padx=10, pady=10)
        self.passwordLabel.config(bg="light grey", fg="white")

        # -----------Entrys------------

        self.desplegable = Desplegable(values, self.frame)
        self.desplegable.grid(row=1, column=0, padx=10, pady=10)

        self.cuadroPassword = tk.Entry(self.frame, show="*", textvariable=self.pw)
        self.cuadroPassword.grid(row=3, column=0, padx=10, pady=10)

        # -----------Buttons-----------

        # Send records button
        self.sendButton = tk.Button(self.frame, text="Enviar", height=1, width=25, bg="SteelBlue1", fg="white",
                                    command=self.send_record)
        self.sendButton.grid(row=4, column=0, padx=10, pady=10)

        # Exit button
        self.quitButton = tk.Button(self.frame, text='Salir', width=25, command=self.close_windows)
        self.quitButton.grid(row=5, column=0)

        self.frame.pack(expand=True)
        self.frame.config(bg="white")

    # Method that sends records information to email in DB
    def send_record(self):
        selected_event = self.desplegable.combo.get()
        self.id_selected_event = selected_event.split('···')[0]
        if send_mail(get_email(self.id_selected_event), str(datetime.now()), get_description(self.id_selected_event),
                  self.pw.get(), get_students_records(self.id_selected_event)):
            messagebox.showinfo("Registros","Correo enviado")

    # Method that destroys current window
    def close_windows(self):
        self.master.destroy()


# Ventana de aplicacion
class InitRecording:
    def __init__(self, master):
        self.master = master

        self.frame = tk.Frame(self.master)
        self.description = tk.StringVar()
        self.email = tk.StringVar()
        self.pw = tk.StringVar()

        self.t_recording = threading.Thread(target=self.recording)

        today = date.today()
        values = get_record_dates(today)

        # -----------Labels------------

        self.descripLabel = tk.Label(self.frame, text="Descripción :")
        self.descripLabel.grid(row=0, column=0, padx=10, pady=10)
        self.descripLabel.config(bg="light grey", fg="white")

        self.passwordLabel = tk.Label(self.frame, text="Contraseña para el envío de resultados :")
        self.passwordLabel.grid(row=3, column=0, padx=10, pady=10)
        self.passwordLabel.config(bg="light grey", fg="white")

        # -----------Entrys------------

        self.desplegable = Desplegable(values, self.frame)
        self.desplegable.grid(row=1, column=0, padx=10, pady=10)

        self.cuadroPassword = tk.Entry(self.frame, show="*", textvariable=self.pw)
        self.cuadroPassword.grid(row=4, column=0, padx=10, pady=10)

        # -----------Buttons-----------

        # Init recording button
        self.initButton = tk.Button(self.frame, text="Iniciar a registrar", height=1, width=25, bg="SteelBlue1",
                                    fg="white", command=self.initRecording)
        self.initButton.grid(row=2, column=0, padx=10, pady=10)

        # Stop recording button
        self.endButton = tk.Button(self.frame, text="Parar de registrar", height=1, width=25, bg="SteelBlue1",
                                   fg="white", command=self.finishRecording)
        self.endButton.grid(row=5, column=0, padx=10, pady=10)

        # Exit button
        self.quitButton = tk.Button(self.frame, text='Salir', width=25, command=self.close_windows)
        self.quitButton.grid(row=6, column=0)

        self.frame.pack(expand=True)
        self.frame.config(bg="white")

    # Method that records tags til time expires or stopped
    def recording(self):
        timeout = timedelta(hours=1)
        finishtime = datetime.now() + timeout
        while datetime.now() < finishtime and NFC_tag.continue_reading:
            try:
                self.read_tag()
            except mariadb.Error as Er:
                if Er.errno == 1452:
                    print("Error foreign key")
                if Er.errno == 1062:
                    print("Already recorded")

    # Method that creates thread to record tags if conditions are ok
    def initRecording(self):
        selected_event = self.desplegable.combo.get()
        self.id_selected_event = selected_event.split('···')[0]
        print(self.id_selected_event)
        if not self.t_recording.is_alive() and not NFC_tag.continue_reading and self.id_selected_event:
            NFC_tag.continue_reading = True
            self.t_recording = threading.Thread(target=self.recording)
            self.t_recording.start()
        elif not self.id_selected_event:
            messagebox.showwarning("Iniciar a registrar", "No se ha seleccionado ningún evento")
        else:
            messagebox.showwarning("Iniciar a registrar", "Existe otro proceso activo haciendo uso del lector")

    # Method to stop recording and send results
    def finishRecording(self):
        if NFC_tag.continue_reading:
            NFC_tag.continue_reading = False
        time.sleep(1)
        if send_mail(get_email(self.id_selected_event), str(datetime.now()), get_description(self.id_selected_event),
                  self.pw.get(), get_students_records(self.id_selected_event)):
            messagebox.showinfo("Registro estudiantes","Resultados enviados")
        else:
            messagebox.showinfo("Registro estudiantes","Los resultados no han podido ser enviados")
        print("Recording finished")

    # Methos to record a tag
    def read_tag(self):
        NFC_tag.continue_reading = True
        etiqueta = NFC_tag.NFCTag()
        if etiqueta.is_NFC_tag() and etiqueta.authenticate_nfc():
            name, last_name = get_student_from_db(etiqueta.get_id_m())
            insert_student_record(self.id_selected_event, etiqueta.get_id_m(), name, last_name)
            print(name, last_name)
        else:
            print("No NFC tag")

    # Method to destroy current windows
    def close_windows(self):
        self.master.destroy()


# Ventana de aplicacion
class StudentsAdmin:
    def __init__(self, master):
        self.master = master
        # self.root = root
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
        self.flag = False
        self.t_write = threading.Thread(target=self.write_tag)
        self.t_read = threading.Thread(target=self.read_tag)
        self.t_clear = threading.Thread(target=self.clear_tag)
        self.t_write_db = threading.Thread(target=self.write_from_ddbb)

        self.myID = tk.StringVar()
        self.myName = tk.StringVar()
        self.myLastName = tk.StringVar()

        # -----------Entrys------------

        self.cuadroId = tk.Entry(self.frame1, textvariable=self.myID)
        self.cuadroId.grid(row=0, column=1, padx=10, pady=10)
        self.cuadroId.config(fg="SteelBlue4", justify="right")

        self.cuadroNombre = tk.Entry(self.frame1, textvariable=self.myName)
        self.cuadroNombre.grid(row=1, column=1, padx=10, pady=10)

        self.cuadroApellido = tk.Entry(self.frame1, textvariable=self.myLastName)
        self.cuadroApellido.grid(row=2, column=1, padx=10, pady=10)

        # -----------Labels------------

        self.idLabel = tk.Label(self.frame1, text="Id :")
        self.idLabel.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.idLabel.config(bg="white")

        self.nameLabel = tk.Label(self.frame1, text="Nombre :")
        self.nameLabel.grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.nameLabel.config(bg="white")

        self.last_nameLabel = tk.Label(self.frame1, text="Apellido :")
        self.last_nameLabel.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.last_nameLabel.config(bg="white")

        # -----------Buttons-----------

        # ----------First row----------- 

        # Read NFC tag button
        self.buttonRead = tk.Button(self.frame2, text="Leer NFC Tag", bg="SteelBlue1", fg="white",
                                    command=self.reading_tag)
        self.buttonRead.grid(row=1, column=0, sticky="e", padx=10, pady=10)

        # Write NFC tag button
        self.buttonWrite = tk.Button(self.frame2, text="Escribir NFC Tag", bg="SteelBlue1", fg="white",
                                     command=self.writing_tag)
        self.buttonWrite.grid(row=1, column=1, sticky="e", padx=10, pady=10)

        # Empty NFC tag button
        self.buttonClear = tk.Button(self.frame2, text="Vaciar NFC Tag", bg="SteelBlue1", fg="white",
                                     command=self.clearing_tag)
        self.buttonClear.grid(row=1, column=2, sticky="e", padx=10, pady=10)

        # ----------Second row----------

        # Terminate thread button
        self.buttonStopThread = tk.Button(self.frame2, text="Parar proceso", bg="SteelBlue1", fg="white",
                                          command=self.stop_read_t)
        self.buttonStopThread.grid(row=2, column=0, sticky="e", padx=10, pady=10)

        # Write NFC tag from DB data button
        self.buttonWriteFromDB = tk.Button(self.frame2, text="Escribir NFC desde BD", bg="SteelBlue1", fg="white",
                                           command=self.writing_from_ddbb)
        self.buttonWriteFromDB.grid(row=2, column=1, sticky="e", padx=10, pady=10)

        # Empty entrys fields button
        self.buttonClearFields = tk.Button(self.frame2, text="Vaciar Campos", bg="SteelBlue1", fg="white",
                                           command=self.clear_fields)
        self.buttonClearFields.grid(row=2, column=2, sticky="e", padx=10, pady=10)

        # Exit button
        self.quitButton = tk.Button(self.frame2, text='Salir', width=15, command=self.close_windows)
        self.quitButton.grid(row=3, column=2, sticky="e", padx=10, pady=10)

        self.frame1.pack(expand=True)
        self.frame1.config(bg="white")
        self.frame2.pack(expand=True)
        self.frame2.config(bg="white")

    # Methos to terminate alive secondary threads
    def stop_read_t(self):
        if self.t_read.is_alive() or self.t_write.is_alive() or self.t_clear.is_alive() or self.t_write_db.is_alive() or NFC_tag.continue_reading:
            NFC_tag.continue_reading = False
        time.sleep(1)

    # Method that creates reading tag thread if conditions are ok
    def reading_tag(self):
        # Check no other process in use of RFIO-522
        if not self.t_read.is_alive() and not self.t_write.is_alive() and not self.t_clear.is_alive() and not self.t_write_db.is_alive() and not NFC_tag.continue_reading:
            self.t_read = threading.Thread(target=self.read_tag)
            self.t_read.start()
        else:
            messagebox.showwarning("Leer NFC Tag", "Existe otro proceso activo haciendo uso del lector")
            # print("No reading, other process running")

    # Method that creates writing tag thread if conditions are ok
    def writing_tag(self):
        # Check no other process in use of RFIO-522
        if not self.t_read.is_alive() and not self.t_write.is_alive() and not self.t_clear.is_alive() and not self.t_write_db.is_alive() and not NFC_tag.continue_reading:
            self.t_write = threading.Thread(target=self.write_tag)
            self.t_write.start()
        else:
            messagebox.showwarning("Escribir NFC Tag", "Existe otro proceso activo haciendo uso del lector")
            # print("No writin, other process running")

    # Method that creates clearing tag thread if conditions are ok
    def clearing_tag(self):
        # Check no other process in use of RFIO-522
        if not self.t_clear.is_alive() and not self.t_write.is_alive() and not self.t_clear.is_alive() and not self.t_write_db.is_alive() and not NFC_tag.continue_reading:
            self.t_clear = threading.Thread(target=self.clear_tag)
            self.t_clear.start()
        else:
            messagebox.showwarning("Vaciar NFC Tag", "Existe otro proceso activo haciendo uso del lector")
            # print("No clearing, other process running")

    # Method that creates writing tags from db thread if conditions are ok
    def writing_from_ddbb(self):
        # Check no other process in use of RFIO-522
        if not self.t_write_db.is_alive() and not self.t_clear.is_alive() and not self.t_write.is_alive() and not self.t_clear.is_alive() and not NFC_tag.continue_reading:
            self.t_write_db = threading.Thread(target=self.write_from_ddbb)
            self.t_write_db.start()
        else:
            messagebox.showwarning("Escribir NFC desde DB", "Existe otro proceso activo haciendo uso del lector")
            # print("No writing from DB, other process running")

    # Method to read NFC tag and shows data read
    def read_tag(self):
        try:
            NFC_tag.continue_reading = True
            etiqueta = NFC_tag.NFCTag()
            if etiqueta.is_NFC_tag() and etiqueta.authenticate_nfc():
                self.myID.set(etiqueta.get_id_m())
                name, last_name = get_student_from_db(etiqueta.get_id_m())
                self.myName.set(name)
                self.myLastName.set(last_name)
            else:
                messagebox.showerror("Lectura NFC", "No se ha detectado ninguna tarjeta de ningún alumno")
        except Exception as error:
            print("Se ha producido el siguiente error")
            print(error)
        # End reading process
        NFC_tag.continue_reading = False

    # Method that writes nfc from inserted info in entrys and insert student into DB
    def write_tag(self):
        try:
            NFC_tag.continue_reading = True
            etiqueta = NFC_tag.NFCTag()
            if etiqueta.is_NFC_tag() and etiqueta.write_nfc(self.myID.get()):
                # Database DDBB
                student = [self.myID.get(), self.myName.get(), self.myLastName.get()]
                insert_student_to_db(student, etiqueta.get_uid_to_num())
        except Exception as e:
            print(e)

    # Method that emptys NFC tag data
    def clear_tag(self):
        try:
            NFC_tag.continue_reading = True
            etiqueta = NFC_tag.NFCTag()
            if etiqueta.is_NFC_tag():
                etiqueta.empty_nfc()
        except Exception as e:
            print(e)

    # Method to write NFC one by one from students DB table.
    def write_from_ddbb(self):
        data = get_students_from_db()
        # If all students in DB has an associated nfc tag it shows next message and skips writting
        if not data:
            messagebox.showwarning("DB", "Todos los alumnos tienen un NFC tag asignado.")
        else:
            for student in data:
                valor = True
                NFC_tag.continue_reading = True
                etiqueta = NFC_tag.NFCTag()
                print("El alumno : " + str(student[0]) + " " + student[1] + " " + student[2])
                if etiqueta.is_NFC_tag() and etiqueta.write_nfc(student[0]):
                    set_student_nfc_true(student, etiqueta.get_uid_to_num())
                    valor = messagebox.askokcancel("Escritor NFC",
                                                   "Alumno escrito:" + str(student[0]) + " " + student[1] +
                                                   " " + student[2] + "\nSepare el NFC tag del lector y pulse 'Ok' "
                                                                      "para escribir el siguiente")
                else:
                    break
                if not valor:
                    break
            messagebox.showinfo("BBDD", "Alumnos registrados")

    # Method to clear entrys fields
    def clear_fields(self):
        self.myID.set("")
        self.myName.set("")
        self.myLastName.set("")

    # Methos to destroy current window
    def close_windows(self):
        self.master.destroy()


def main():
    root = tk.Tk()
    root.title("ETSIDI Asistencia")
    root.geometry("600x350")
    root.config(bg='white')
    app = MainMenu(root)
    root.mainloop()


if __name__ == '__main__':
    main()
