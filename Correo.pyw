import sys
import re
import time
import datetime
import smtplib
import pymysql

####################CORREO##########################
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image, ImageWin


def EnviarEmailPassword(Remitente, Destinatario, UsuarioSMTP, PuertoSMTP, ContrasenaSMTP, ContrasenaCorreo):
    try:
        fromaddr = Remitente
        toaddr = Destinatario

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Reposicion de contrasena"
        
        body = "Se ha realizado un cambio de contrase;a desde la aplicacion de Daniel Lopez\n Su  contrase;a es: " + str(ContrasenaCorreo)
        
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(UsuarioSMTP, PuertoSMTP)
        server.starttls()
        server.login(fromaddr, ContrasenaSMTP)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    except Exception as e:
    	print("Error en la funcion de envio de correo dentro de correo.pyw")



def EnviarEmailConArchivo(Remitente,Destinatario,Asunto,NombreArchivo,RutaArchivo):
	fecha=time.srtftime("%d/%m/%y")
	fromaddr = Remitente
	toaddr = Destinatario

	msg = MIMEMultipart()

	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = Asunto

	body ="Reporte del dia "+fecha

	msg.attach(MIMEText(body, 'plain'))

	filename = NombreArchivo
	attachment = open(RutaArchivo+"/"+NombreArchivo, "rb")

	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

	msg.attach(part)

	server = smtplib.SMTP('smtp.live.com', 587)
	server.starttls()
	server.login(fromaddr, "D3n10zp8")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
