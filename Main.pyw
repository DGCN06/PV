import datetime
import re
import sys
import os
import time
import uuid
import webbrowser
import shutil
####################BASE DE DATOS###################
from configparser import ConfigParser
from PyQt5.sip import delete
import requests
from requests.models import Response
import Correo
import pymysql
######################INTERFAZ#######################
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import QRegExp, QUrl, Qt
from PyQt5.QtGui import QPixmap, QRegExpValidator, QWindow
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QCompleter, QDial, QDialog,
                             QFileDialog, QGridLayout, QLabel, QLineEdit,
                             QListWidgetItem, QMainWindow, QMessageBox,
                             QPushButton, QSpinBox, QTableWidgetItem, QTextEdit,
                             QVBoxLayout, QWidget)


####################Clases Generales################

class MostrarMensaje(QDialog):
    """docstring for MostrarError."""

    def __init__(self):
        QDialog.__init__(self)

    def MostrarError(self, Titulo, Mensaje):
        QMessageBox.critical(self, str(Titulo), str(Mensaje), QMessageBox.Ok)
        self.EscribirEnLog("Error", Mensaje)

    def MostrarAdvertencia(self, Titulo, Mensaje):
        QMessageBox.warning(self, str(Titulo), str(Mensaje), QMessageBox.Ok)
        self.EscribirEnLog("Advertencia", Mensaje)

    def EscribirEnLog(self, Tipo, e):
        try:
            print("Escribir en log")
            archivo = open("Config/Log.txt", "r+")
            contenido = archivo.read()
            final_de_archivo = archivo.tell()
            archivo.write(time.strftime("%I:%M:%S") +
                          "     "+Tipo+": "+str(e)+"\n\n")
            archivo.seek(final_de_archivo)
        except Exception as e:
            print("El programa no se detiene porque: "+str(e))


class ConfigurarConexion(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/Conexion.ui", self)
        self.pushButton_Guardar.clicked.connect(self.Guardar)

    def CargarConfiguracion(self):
        try:
            config = ConfigParser()
            config.read("Config\Configuraciones.ini")
            host = config['BDD']['Servidor']
            port = config['BDD']['Puerto']
            user = config['BDD']['Usuario']
            db = config['BDD']['NombreBDD']
            passw = config['BDD']['Pass']
            self.lineEdit_NombreServidor.setText(host)
            self.lineEdit_Puerto.setText(port)
            self.lineEdit_BD.setText(db)
            self.lineEdit_Usuario.setText(user)
            self.lineEdit_Password.setText(passw)

        except Exception as e:
        	MostrarMensaje.MostrarError(
        	    "Archivo de configuracion", "No se puede cargar el archivo de configuracion\nVerifique que el archivo exista en la ruta /conf\n"+str(e))

    def Guardar(self):
        try:
            config = ConfigParser()
            config.read("Config\Configuraciones.ini")
            config.set("BDD", "Servidor", self.lineEdit_NombreServidor.text())
            config.set("BDD", "Puerto", self.lineEdit_Puerto.text())
            config.set("BDD", "NombreBDD", self.lineEdit_BD.text())
            config.set("BDD", "Usuario", self.lineEdit_Usuario.text())
            config.set("BDD", "Pass", self.lineEdit_Password.text())
            config.write(open("Config\Configuraciones.ini", "w"))
            ReiniciarAplicacion = QMessageBox.question(
                self, "Reiniciar la aplicacion", "Para que se reflejen los cambios, es necesario reiniciar la aplicacion\nDesea hacerlo en este momento?", QMessageBox.Yes | QMessageBox.No)
            if ReiniciarAplicacion == QMessageBox.Yes:
                ConfigurarConexion.close()
                Login.close()
                MostrarMensaje.EscribirEnLog(
                    "Eleccion", "Reinicio la aplicacion para tomar los cambios de la base de datos")
        except Exception as e:
            MostrarMensaje.MostrarError(
                "Guardar Configuracion", "No se puede guardar la configuracion se recomienda realizar manualmente la configuracion desde el archivo txt ubicado en /conf\n"+str(e))


class Activacion(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/Activacion.ui", self)
        self.pushButton_Aceptar.clicked.connect(self.Aceptar)
        self.pushButton_NuevaCuenta.clicked.connect(self.NuevaCuenta)
        self.pushButton_OlvidePass.clicked.connect(self.OlvidarPass)

    def OlvidarPass(self):
        print("Click en pass")
        webbrowser.open_new("http://127.0.0.1:4000/OlvidePass")

    def Aceptar(self):
        activo = obtener_licencia(
            self.lineEdit_Correo.text(), self.lineEdit_Password.text())
        print("Esta activo:" + activo)
        if activo == '1':
            Activacion.close()
            IniciaAPP()

    def NuevaCuenta(self):
        webbrowser.open_new("http://127.0.0.1:4000/Registrarse")


##################Clases de aplicación###############

id_usuario_actual = 0
tipo_usuario_actual = 1


class Login(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/Login.ui", self)
        self.pushButton_Ingresar.clicked.connect(self.Ingresar)
        self.pushButton_Cancelar.clicked.connect(self.close)
        self.pushButton_Olivido_Password.clicked.connect(self.OlvidoPass)
        self.pushButton_ConfigurarConexion.clicked.connect(
            self.ConfigurarConexion)
        self.lineEdit_Usuario.setText("Administrador")
        self.lineEdit_Pass.setText("1234")
        try:
            pixmap = QPixmap('Config/logo.png')
            self.label_Logo.setPixmap(pixmap)
        except Exception as e:
            MostrarMensaje.MostrarError(
                self, "Asignacion de logo", "No se pudo Asignar el logo, asegurese de que exista el archivo Logo.PNG en la ruta de configuracion\n"+str(e))

    def OlvidoPass(self):
        try:
            usuario = self.lineEdit_Usuario.text()
            print("imprimiendo a usuario", usuario)
            if usuario != "" and usuario != None:
                correo_usuario, password_usuario = ObtenerCorreoUsuario(
                    usuario)
                if correo_usuario != False:
                    servidor_smtp, puerto_smtp, correo_corr, pass_corr = ObtenerConfiguracionCorreo()
                    Correo.EnviarEmailPassword(
                        correo_corr, correo_usuario, servidor_smtp, puerto_smtp, pass_corr, password_usuario)
                    MostrarMensaje.MostrarAdvertencia(
                        "PasswordEnviado", "Se le envio su password al correo, por favor revisarlo")
                else:
                    MostrarMensaje.MostrarAdvertencia(
                        "PasswordEnviado", "Se le envio su password al correo, por favor revisarlo,0")
            else:
                MostrarMensaje.MostrarAdvertencia(
                    "Usuario invalido", "Por favor ingresa un usuario valido")
        except Exception as e:
            MostrarMensaje.MostrarError(
                "Envio de correo", "Ocurrio un problema al enviar el correo con la contraseña, favor de verificar los datos del correo\n"+str(e))

    def Ingresar(self):
        try:
            global id_usuario_actual
            global tipo_usuario_actual
            cur = conn.cursor()
            cur.execute("SELECT id_usuario,id_perfil,pass,correo from usuario where nombre=%s and pass=%s",
                        (self.lineEdit_Usuario.text(), self.lineEdit_Pass.text()))
            result = cur.fetchone()
            if result != None:
                id_usuario_actual = result[0]
                tipo_usuario_actual = result[1]
                print(result)
                Login.close()
                Menu.showMaximized()
            else:
                MostrarMensaje.MostrarAdvertencia(
                    "Login", "Por favor Validar los datos de usuario y contrase;a\n")
        except Exception as e:
            MostrarMensaje.MostrarError(
                "Login", "Por favor Validar los datos de usuario y contrase;a\n"+str(e))
        finally:
            cur.close()

    def SinContra(self):
        self.lineEdit_Pass.setText("")

    def ConfigurarConexion(self):
        try:
            ConfigurarConexion.CargarConfiguracion()
            ConfigurarConexion.showNormal()
        except Exception as e:
            MostrarMensaje.MostrarError(
                "Conexion A Base de datos", "No se puede mostrar la conexion a la base de datos\nSe recomienda realizar la modificacion manualmente\n"+str(e))


class Menu(QWidget):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/Menu.ui", self)
        try:
            pixmap = QPixmap('Config/logo.png')
            self.label_Logo.setPixmap(pixmap)
        except Exception as e:
            MostrarMensaje.MostrarError(
                self, "Asignacion de logo", "No se pudo Asignar el logo, asegurese de que exista el archivo Logo.PNG en la ruta de configuracion\n"+str(e))
        self.pushButton_Producto.clicked.connect(self.abrirCrearProducto)
        self.pushButton_BuscarProducto.clicked.connect(self.verProducto)
        self.pushButton_Impuesto.clicked.connect(self.impuestos)
        self.pushButton_Salir.clicked.connect(self.cerrar)
        self.pushButton_Ticket.clicked.connect(self.modificarticket)

    def modificarticket(self):
        ModificarTicket.cargardatos()
        ModificarTicket.showNormal()

    def verProducto(self):
        Ver_Producto.limpiarDatos()
        Ver_Producto.cargarDatos()
        Ver_Producto.showMaximized()

    def abrirCrearProducto(self):
        Crear_Producto.limpiar_Ventana()
        Crear_Producto.showNormal()

    def impuestos(self):
        Impuestos.cargardatos()
        Impuestos.showNormal()

    def cerrar(Self):
        Menu.close()
        global id_usuario_actual
        global tipo_usuario_actual
        id_usuario_actual = 0
        tipo_usuario_actual = 0
        Login.showNormal()


class Impuestos(QWidget):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/Tipoimpuesto.ui", self)
        self.lineEdit_Porcentaje.setValidator(QtGui.QDoubleValidator())
        self.pushButton_Agregar.clicked.connect(self.agregarImpuestoBase)
        self.pushButton_Eliminar.clicked.connect(self.eliminarImpuestoBase)

    def limpiarTablaImpuestos(self):
        while self.tableWidget_Impuesto.rowCount() > 0:
            self.tableWidget_Impuesto.removeRow(0)
        self.lineEdit_Porcentaje.setText("")
        self.lineEdit_NombreImpuesto.setText("")

    def cargardatos(self):
        try:
            self.limpiarTablaImpuestos()
            i = 0
            cur = conn.cursor()
            cur.execute("SELECT nombre,porcentaje from impuesto")
            for row in cur:
                print(row)
                self.tableWidget_Impuesto.insertRow(i)
                self.tableWidget_Impuesto.setItem(
                    i, 0, QTableWidgetItem(str(row[0])))
                self.tableWidget_Impuesto.setItem(
                    i, 1, QTableWidgetItem(str(row[1])))
                i = i+1
            cur.close()
        except Exception as e:
            print(e)

    def agregarImpuestoBase(self):
        resultado = [0, "OK"]
        nombre = self.lineEdit_NombreImpuesto.text()
        porcentaje = self.lineEdit_Porcentaje.text()
        if nombre != "" and porcentaje != "":
            resultado = GuardarImpuestoBase(nombre, porcentaje)
        if resultado[0] == -99:
            MostrarMensaje.MostrarError(
                "Error al guardar el impuesto", resultado[1])
        else:
            self.cargardatos()

    def eliminarImpuestoBase(self):
        resultado = [0, "Sin acción"]
        impuesto = self.tableWidget_Impuesto.selectedItems()[0].text()
        resultado = eliminarImpuestoBase(impuesto)
        print(resultado)
        if resultado[0] == -99:
            MostrarMensaje.MostrarError(
                "Error al eliminar impuesto", resultado[1])
        else:
            self.cargardatos()


class Crear_Producto(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/AgregarInvent.ui", self)
        self.pushButton_Aceptar.clicked.connect(self.Guardar)
        self.pushButton_Img.clicked.connect(self.CargarImagen)

    def limpiar_Ventana(self):
        for le in self.findChildren(QLineEdit):
            le.clear()
        for lbl in self.findChildren(QComboBox):
            lbl.setCurrentText("")
        for lbl in self.findChildren(QSpinBox):
            lbl.setValue(0)
        self.label_Notificaciones.hide()
        self.label_Img.setText("")
        self.label_Ruta.setText("")

    def Notificar(self, mensaje, tipoMensaje=1):
        self.label_Notificaciones.show()
        self.label_Notificaciones.setText(mensaje)
        if tipoMensaje == "ERROR" or tipoMensaje == -1:
            self.label_Notificaciones.setStyleSheet("font color: red;")
        if tipoMensaje == "ADVERTENCIA" or tipoMensaje == 2:
            self.label_Notificaciones.setStyleSheet("font color: yellow;")
        if tipoMensaje == "CORRECTO" or tipoMensaje == 1:
            self.label_Notificaciones.setStyleSheet("font color: green;")

    def CargarImagen(self):
        try:
            abrirI = QFileDialog.getOpenFileName(
                self, "Seleccione Archivo", os.getcwd(), "All Files (*);;Image Files (*.PNG)")
            fuente = abrirI[0]
            self.label_Ruta.setText(str(fuente))
            pixmap = QPixmap(fuente)
            self.label_Img.setPixmap(pixmap)
        except Exception as e:
            MostrarMensaje.MostrarError("Error al cargar la imagen", str(e))

    def guardarImagen(self):
        try:
            fuente = self.label_Ruta.text()
            extension = fuente.split('.')[1]
            nuevonombreIMG = str(uuid.uuid4())+'.'+str(extension)
            destino = os.getcwdb()+"\interfaz\imagenes\productos\\"+nuevonombreIMG
            shutil.copyfile(fuente, destino)
            return [1, nuevonombreIMG]
        except Exception as e:
            return [-99, str(e)]

    def Guardar(self):
        try:
            saveima = self.guardarImagen()
            guardar = GuardaProducto(self.lineEdit_Codigo.text(), self.lineEdit_Descrip.text(
            ), self.lineEdit_Costo.text(), self.lineEdit_Precio.text(), saveima[1])
            if guardar[0] != -99:
                mov_inventario = GuardarMovimientoInventario(
                    0, 0, self.lineEdit_Codigo.text(), self.spinBox.value(), self.lineEdit_Costo.text())
                if mov_inventario[0] != -99:
                   self.Notificar(
                       "Producto guardado correctamente", "CORRECTO")
                else:
                    MostrarMensaje.MostrarError(
                        "Error al guardar el producto", mov_inventario[1])
            else:
                MostrarMensaje.MostrarError(
                    "Error al guardar el producto", guardar[1])
        except Exception as e:
            MostrarMensaje.MostrarError("Error al guardar el producto", str(e))


class Ver_Producto(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/BuscarProducto.ui", self)
        self.comboBox_Codigo.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.pushButton_Buscar.clicked.connect(self.buscar)
        self.pushButton_Eliminar.clicked.connect(self.eliminarProducto)
        self.tableWidget.itemDoubleClicked.connect(self.modificarProducto)
        self.pushButton_Modificar.clicked.connect(self.modificarProducto)

    def limpiarDatos(self):
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        self.comboBox_Codigo.clear()

    def buscar(self):
        self.tableWidget.setCurrentItem(None)
        s = self.comboBox_Codigo.currentText()
        matching_items = self.tableWidget.findItems(s, Qt.MatchContains)
        if matching_items:
            # We have found something.
            item = matching_items[0]  # Take the first.
            self.tableWidget.setCurrentItem(item)

    def cargarDatos(self):
        try:
            i = 0
            cur = conn.cursor()
            cur.execute(
                "SELECT id_producto,codigo,descripcion,costo,precio,imagen from producto")
            for row in cur:
                print(row)
                self.tableWidget.insertRow(i)
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row[1])))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(row[2])))

                entradas = obtener_entradas_salidas_producto(row[1], 0)[0]
                salidas = obtener_entradas_salidas_producto(row[1], 1)[0]
                existencia = int(entradas)-int(salidas)
                self.tableWidget.setItem(
                    i, 2, QTableWidgetItem(str(existencia)))

                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(row[4])))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(row[5])))
                self.comboBox_Codigo.addItem(row[1])
                self.comboBox_Codigo.addItem(row[2])
                i = i+1
            self.comboBox_Codigo.setCurrentText("")
            cur.close()
        except Exception as e:
            print(e)

    def eliminarProducto(self):
        elementoseleccionado = self.tableWidget.currentRow()
        codigo_producto = self.tableWidget.selectedItems()[0].text()
        eliminado = eliminar_Producto(codigo_producto)
        print(eliminado)
        if eliminado[0] != 1:
            MostrarMensaje.MostrarError(
                "Error al eliminar el producto", eliminado[1])
        else:
            self.tableWidget.removeRow(elementoseleccionado)

    def modificarProducto(self):
        if self.tableWidget.currentRow() > 0:
            Modificar_Producto.cargarDatos(
                self.tableWidget.selectedItems()[0].text())
            Modificar_Producto.showNormal()


class Modificar_Producto(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/AgregarInvent.ui", self)
        self.pushButton_Aceptar.clicked.connect(self.guardar)

    def Notificar(self, mensaje, tipoMensaje=1):
        self.label_Notificaciones.show()
        self.label_Notificaciones.setText(mensaje)
        if tipoMensaje == "ERROR" or tipoMensaje == -1:
            self.label_Notificaciones.setStyleSheet("font color: red;")
        if tipoMensaje == "ADVERTENCIA" or tipoMensaje == 2:
            self.label_Notificaciones.setStyleSheet("font color: yellow;")
        if tipoMensaje == "CORRECTO" or tipoMensaje == 1:
            self.label_Notificaciones.setStyleSheet("font color: green;")

    def guardar(self):
        try:
            saveima = [-99, "None"]
            if self.label_Ruta.text() != '':
                saveima = self.guardarImagen()
            guardar = ModificaProducto(self.lineEdit_Codigo.text(), self.lineEdit_Descrip.text(
            ), self.lineEdit_Costo.text(), self.lineEdit_Precio.text(), saveima[1])
            if guardar[0] != -99:
                self.Notificar("Producto guardado correctamente", "CORRECTO")
            else:
                MostrarMensaje.MostrarError(
                    "Error al guardar el producto", guardar[1])
        except Exception as e:
            MostrarMensaje.MostrarError("Error al guardar el producto", str(e))

    def guardarImagen(self):
        try:
            fuente = self.label_Ruta.text()
            extension = fuente.split('.')[1]
            nuevonombreIMG = str(uuid.uuid4())+'.'+str(extension)
            destino = os.getcwdb()+"\interfaz\imagenes\productos\\"+nuevonombreIMG
            shutil.copyfile(fuente, destino)
            return [1, nuevonombreIMG]
        except Exception as e:
            return [-99, str(e)]

    def cargarDatos(self, producto):
        try:
            self.limpiar_Ventana()
            datos = Obtener_Datos_Producto_Registro(producto)
            if datos != None:
                if datos[1] == 'OK' and datos != None:
                    d = datos[0]
                    print(d)
                    self.lineEdit_Codigo.setText(d[0])
                    self.lineEdit_Codigo.setEnabled(False)

                    self.lineEdit_Descrip.setText(d[1])
                    self.spinBox.setValue(d[2])
                    self.spinBox.setEnabled(False)
                    self.lineEdit_Costo.setText(str(d[3]))
                    self.lineEdit_Precio.setText(str(d[4]))
                    imagen = os.getcwd() + \
                                       "\\interfaz\\imagenes\\productos\\"+d[5]
                    print(imagen)
                    self.label_Img.setPixmap(QPixmap(imagen))

                else:
                    MostrarMensaje.MostrarError(
                        "Error al cargar los datos del producto", datos[1])
            else:
                MostrarMensaje.MostrarAdvertencia(
                    "Error al cargar los datos del producto", "Producto incorrecto o nonetype")
        except Exception as e:
            MostrarMensaje.MostrarError(
                "Error al cargar los datos del producto", e)

    def limpiar_Ventana(self):
        for le in self.findChildren(QLineEdit):
            le.clear()
        for lbl in self.findChildren(QComboBox):
            lbl.setCurrentText("")
        for lbl in self.findChildren(QSpinBox):
            lbl.setValue(0)
        self.label_Notificaciones.hide()
        self.label_Img.setText("")
        self.label_Ruta.setText("")


class ModificarTicket(QDialog):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi("interfaz/Ticket.ui", self)
        self.pushButton_Cancelar.clicked.connect(self.close)
        self.pushButton_Aceptar.clicked.connect(self.Guardar)
        self.pushButton_Ticket.clicked.connect(self.prueba)
  
  
    def cargardatos(self):
        try:
            cur=conn.cursor()
            cur.execute("Select ticketencabezado,ticketpie from configuracion")
            for row in cur:
                self.textEdit_Encabezado.setPlainText(row[0])
                self.textEdit_Pie.setPlainText(row[1])
            cur.close()
        except Exception as e:
            MostrarMensaje.MostrarError("Error al cargar el ticket",e)
    
    def Guardar(self):
        try:
            Encabezado = self.textEdit_Encabezado.toPlainText()
            Pie = self.textEdit_Pie.toPlainText()
            resultado=actualizarticket(Encabezado,Pie)
            if resultado[0]!=-99:
                ModificarTicket.close()
            else:
                MostrarMensaje.MostrarError("Error al guardar los datos del ticket", resultado[1])
        except Exception as e:
            QMessageBox.critical(self,"Error","No se pudo guardar la configuracion del ticket\n"+str(e),QMessageBox.Ok)
            
            
    def prueba(self):
        try:
            ImprimirEncabezado()
            ImprimirPie()
            cortar()
        except Exception as e:
            QMessageBox.critical(self,"Error","No se pudo imprimir el ticket\n"+str(e),QMessageBox.Ok)

    
class Probar_UI(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        uic.loadUi("interfaz/Venta.ui",self)

#################### Funciones Obtener###############
def ObtenerCorreoUsuario(usuario):
    try:
        correo=""
        cur=conn.cursor()
        cur.execute("SELECT correo,pass from usuario where nombre=%s",(usuario))
        for row in cur:
            return row[0],row[1]
            cur.close()
        return False
    except Exception as e:
        MostrarMensaje.MostrarError("Obtener Correo del usuario","No se pudo obtener el correo del usuario, por favor verifica que el nombre de usuario sea correcto"+str(e))
    finally:
        cur.close()

def ObtenerConfiguracionCorreo():
    try:
        cur=conn.cursor()
        cur.execute("SELECT ServidorSMTP,puertoSMTP,CorreoSMTP,PassSMTP from Configuracion")
        for row in cur:
            return row[0],row[1],row[2],row[3]
            cur.close()
    except Exception as e:
        MostrarMensaje.MostrarError("Configuracion de Correo","No se pudo obtener la configuracion de correo.\nPor favor solicitar al administrador del sistema que se verifique dicha informacion\n"+str(e))
    finally:
        cur.close()


################### Funciones de guardar en BDD##################
def GuardaProducto(codigo=0,descripcion='',costo=0,precio=0,imagen=''):
    try:
        cur=conn.cursor()
        cur.execute("INSERT INTO producto(codigo,descripcion,costo,precio,imagen) VALUES(%s,%s,%s,%s,%s)",(codigo,descripcion,costo,precio,imagen))
        cur.close()
        return [1,'OK']
    except Exception as e:
        return [-99,str(e)]

def GuardarMovimientoInventario(tipomovimiento=0,motivomovimiento=0,producto='',cantidad=0,importe=0):
    try:
        cur=conn.cursor()
        cur.execute("INSERT INTO movimiento_inventario(tipo_movimiento,motivo_movimiento,fecha,producto,cantidad,importe) VALUES(%s,%s,curdate(),%s,%s,%s)",(tipomovimiento,motivomovimiento,producto,cantidad,importe))
        cur.close()
        return [1,'OK']
    except Exception as e:
        return [-99,str(e)]

def ModificaProducto(codigo=0,descripcion='',costo=0,precio=0,imagen=''):
    try:
        cur=conn.cursor()
        cur.execute("UPDATE producto set descripcion=%s, costo=%s, precio=%s, imagen=%s where codigo=%s",(descripcion,costo,precio,imagen,codigo))
        cur.close()
        return [1,'OK']
    except Exception as e:
        return [-99,str(e)]    

def GuardarImpuestoBase(nombre,porcentaje):
    try:
        cur=conn.cursor()
        cur.execute("INSERT INTO Impuesto(Nombre,porcentaje) VALUES(%s,%s)",(nombre,porcentaje))
        cur.close()
        return [1,'OK']
    except Exception as e:
        return [-99,str(e)]   


def actualizarticket(encabezado,pie):
    try:
        cur=conn.cursor()
        cur.execute("Update configuracion set ticketencabezado=%s,ticketpie=%s",(encabezado,pie))
        return [1,"Ok"]
    except Exception as e:
        cur.close()
        return [-99,e]

###################### Funciones para consultar en BDD################
def Obtener_Datos_Producto_Registro(producto=''):
    try:
        cur=conn.cursor()
        cur.execute("SELECT Codigo,descripcion,cantidad,costo,precio,imagen from producto pro inner join movimiento_inventario inv ON inv.producto=pro.codigo where pro.codigo=%s and motivo_movimiento=0",(producto))
        for row in cur:
            cur.close()
            return [row,"OK"]
    except Exception as e:
        cur.close()
        return [-99,e]

def obtener_entradas_salidas_producto(producto='',tipomovimiento='0'):
    try:
        cantidad=0
        cur=conn.cursor()
        cur.execute("SELECT sum(cantidad) FROM movimiento_inventario where producto=%s and tipo_movimiento=%s",(producto,tipomovimiento))
        for row in cur:
            if row[0]!=None:
                cantidad=row[0]
            else:
                cantidad=0
        cur.close()
        return [cantidad,"OK"]
    except Exception as e:
        print(e)
        cur.close()
        return [0,str(e)]

def ObtenerImpuestos():
    try:
        cur=conn.cursor()
        cur.execute("SELECT Nombre,Porcentaje from impuesto")
        for row in cur:
            cur.close()
            return [row,"OK"]
    except Exception as e:
        cur.close()
        return [-99,e]    

####################### Funciones para eliminar en BDD################
def eliminar_Producto(producto=''):
    try:
        esPosible=0
        cur=conn.cursor()
        cur.execute("SELECT count(id_movimiento) from movimiento_inventario where producto=%s",(producto))
        for row in cur:
            if int(row[0])<=1:
                esPosible=1
        if esPosible==1:
            print("si elimina")
            cur.execute("DELETE FROM producto where codigo=%s",(producto))
            cur.execute("DELETE FROM movimiento_inventario where producto=%s",(producto))
        cur.close()
        return [1,"OK"]
    except Exception as e:
        cur.close()
        print(e)
        return [-99,e]
            
def eliminarImpuestoBase(impuesto):
    try:
        usado=0
        cur=conn.cursor()
        cur.execute("SELECT count(idimpuestos_conjunto) from impuestos_conjunto where Impuesto=%s",(impuesto))
        for row in cur:
            if row[0]>0:
                usado=1
        if usado==0:
            cur.execute("DELETE FROM impuesto where Nombre=%s",(impuesto))
            cur.close()
            return [1,"OK"]
        else:
            return [0,"El impuesto se encuentra asignado a un conjunto de impuestos"]
    except Exception as e:
        return [-99,e]
        

######################## Valida licenciamiento ###########################

def valida_licencia():
    try:
        WS=config['Licenciamiento']['WS']
        CodigoLicencia=config['Licenciamiento']['Licencia']
        CodigoEquipo=config['Licenciamiento']['Equipo']
        url_licencia=str(WS)+'/'+str(CodigoLicencia)+'/'+CodigoEquipo
        print(url_licencia)
        licenciamiento = requests.get(url_licencia)
        resultado=licenciamiento.json()['codigo']
        mensaje=licenciamiento.json()['mensaje']
        return resultado,mensaje
    except Exception as e:
        MostrarMensaje.MostrarError("Error al validar la licencia", "Por favor verifica que se tenga acceso a internet y que no existan \nbloqueos por las aplicaciones de antivirus\n"+str(e) )
        return -1,-1
def valida_licencia_activa():
    try:
        numlicencia=config['Licenciamiento']['Licencia']
        if numlicencia=='' or numlicencia=='0':
            return 0
        else:
            return 1
    except Exception as e:
        MostrarMensaje.MostrarError("Error de licenciamiento","Error al leer la Configuración de su licencia, por favor revise que exista el archivo de configuraciones\n" + str(e))
        return -1

def valida_primer_ingreso():
    try:
        print("1.1")
        CodigoEquipo=config['Licenciamiento']['equipo']
        print("1.2")
        print(CodigoEquipo)
        if CodigoEquipo=='0' or CodigoEquipo=='':
            print ("1.3")
            config.set("Licenciamiento","equipo",str(uuid.uuid4()))
            print ("1.4")
            config.set("Licenciamiento","nombre",os.environ['COMPUTERNAME'])
            print ("1.5")
            config.write(open("Config\Configuraciones.ini","w"))
            print ("1.6")
            return 0
        return 1
    except Exception as e:
        MostrarMensaje.MostrarError("Error de licenciamiento","Error al leer la Configuración de su licencia, por favor revise que exista el archivo de configuraciones\n de lo contrario reinicie la aplicacion" + str(e))
        return -1

def obtener_licencia(correo,passw):
    try:
        WS=config['Licenciamiento']['wsusuario']
        url=WS+'/'+correo+'/'+passw
        print(url)
        licenciamiento = requests.get(url)
        print(licenciamiento)
        codigo=licenciamiento.json()['codigo']
        mensaje=licenciamiento.json()['mensaje']
        print(codigo)
        print(mensaje)
        if codigo!='99':
            if codigo=='1':
                config.set("Licenciamiento","licencia",mensaje)
                config.write(open("Config\Configuraciones.ini","w"))
                return codigo
            else:
                MostrarMensaje.MostrarError("Problema en licenciamiento",str(mensaje) )
                return codigo
        else:
            MostrarMensaje.MostrarError("Problema en licenciamiento",str(mensaje) )
    except Exception as e:
        MostrarMensaje.MostrarError("Acceso a licencia","No se puede comprobar la licencia, verifique su conexión a internet: "+str(e) )
        
def registraEquipo():
    try:
        WS=config['Licenciamiento']['WS']
        numero_licencia=config['Licenciamiento']['licencia']
        numero_equipo=config['Licenciamiento']['equipo']
        nombre_equipo=config['Licenciamiento']['nombre']
        url=WS+'/'+numero_licencia+'/'+numero_equipo+'/'+nombre_equipo
        print(url)
        licenciamiento = requests.get(url)
        resultado=licenciamiento.json()['codigo']
        mensaje=licenciamiento.json()['mensaje']
        if resultado!=-1 or resultado!= '99':
            print (licenciamiento)
            print (resultado)
            print (mensaje)
            return resultado,mensaje
    except Exception as e:
        resultado='99'
        mensaje=str(e)
        return resultado,mensaje
    
def IniciaAPP():   
    try:
        print("1")
        EquipoActivo=valida_primer_ingreso()
        print("2")
        validalicenciaactiva=valida_licencia_activa()
        print("3")
        licenciamientovalido=0
        if EquipoActivo!=-1 or validalicenciaactiva==-1:
            if validalicenciaactiva==0:
                print("valida licencia 0")
                Activacion.showNormal()
            if validalicenciaactiva==1:
                print("valida licencia 1")
                #licenciavalida,mensaje=valida_licencia()
                licenciavalida,mensaje="1",""
                print(licenciavalida)
                print(mensaje)
                if licenciavalida=='0':
                    MostrarMensaje.MostrarError("Sin licencia",mensaje)
                    sys.exit()
                if licenciavalida=='1':
                    print("todo ok")
                    Login.showNormal()
                if licenciavalida=='2':
                    print("entro en el 2")
                    MostrarMensaje.MostrarError("Sin licencia",mensaje + "\n llame al area de ventas para adquirir una nueva licencia")
                    
                if licenciavalida=='3':
                    MostrarMensaje.MostrarError("Sin licencia",mensaje)
                    print("ya se va a cerrar")
                    sys.exit()
                    print("Ya debio cerrarse")
                    # Indicar al usuario que active este equipo en la Pagina
                if licenciavalida=='4':
                    MostrarMensaje.MostrarAdvertencia("Sin licencia",mensaje)
                    codigoderegistro,mensajeregistro=registraEquipo()
                    if codigoderegistro!='99':
                        if codigoderegistro=='5':
                            MostrarMensaje.MostrarAdvertencia("Equipo registrado correctamente",mensajeregistro)
                            IniciaAPP()
                        if codigoderegistro=='6':
                            MostrarMensaje.MostrarAdvertencia("Equipo registrado correctamente",mensajeregistro)
                            IniciaAPP()
                    else:
                        MostrarMensaje.MostrarAdvertencia("Problema al registrar el equipo",mensajeregistro)    
        else:
            MostrarMensaje.MostrarError("Acceso a archivo de configuración","No se puede comprobar la licencia" )  
            
    except Exception as e:
        print(e)
        sys.exit()
    

#################### Declaración de clases #######################
app = QApplication(sys.argv)
Login=Login()
Menu=Menu()
Impuestos=Impuestos()


ConfigurarConexion=ConfigurarConexion()
MostrarMensaje=MostrarMensaje()
Activacion=Activacion()
ModificarTicket=ModificarTicket()


Crear_Producto=Crear_Producto()
Ver_Producto=Ver_Producto()
Modificar_Producto=Modificar_Producto()
Probar_UI=Probar_UI()




######################  Conexión a BDD ########################

try:
    config = ConfigParser()
    config.read("Config\Configuraciones.ini")
    host=config['BDD']['Servidor']
    port=config['BDD']['Puerto']
    user=config['BDD']['Usuario']
    db=config['BDD']['NombreBDD']
    passw=config['BDD']['Pass']
    
    
except Exception as e:
	MostrarMensaje.MostrarError("Archivo de configuracion",e)

try:
	conn = pymysql.connect(host=str(host), port=int(port), user=str(user), passwd=str(passw), db=str(db),autocommit=True)
except Exception as e:
    print("LLEGO AL ERROR")
    MostrarMensaje.MostrarError("Conexion de base de datos","Error al conectar a la base de datos\nPor favor revisar la configuracion desde el boton de configurar\nO revisar archivo de base de datos ubicado en la carpeta Config\n"+str(e))
    Login.pushButton_Ingresar.setEnabled(False)



######################  Inicia Aplicacion ########################
IniciaAPP()
sys.exit(app.exec())

    
    
    
    


