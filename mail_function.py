#!/usr/bin/python
"""mail_function.py: Funciones para realizar el envío de resultados por email"""
__author__ = "Ana María Manso Rodríguez"
__credits__ = ["Ana María Manso Rodríguez"]
__version__ = "1.0"
__status__ = "Development"

import smtplib
import ssl
from email.message import EmailMessage


def send_mail(receiver_email, date, description, password, df_csv):
    port = 465
    msg = EmailMessage()
    msg['Subject'] = "ETSIDI Asistencia %s" % description
    msg['From'] = 'attendancesystem97@gmail.com'
    msg['To'] = receiver_email
    message = "ETSIDI ASISTENCIA \n \n Alumnos registrados fecha : " + date
    msg.set_content(message)
    
    excel_name = description + ' registros.csv'
    df_csv.to_csv(excel_name)
    
    with open(excel_name, 'rb') as content_file:
        content = content_file.read()
        msg.add_attachment(content, maintype='application', subtype='csv', filename='students.csv')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        try:
            server.login("attendancesystem97@gmail.com", password)
            server.send_message(msg)
            print("Email sent")
            return True
        except Exception as e:
            print(e)
            return False
    
