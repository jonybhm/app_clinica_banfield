# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""
# main.py
import auxiliar.debug.logger  # activa logging y excepthook
import logging
import sys, time, os, ctypes
from workers.base.task_manager import TaskManager  
from workers.base.base_task import BaseTask  
import resources_rc

logging.info("Iniciando aplicación...")

def es_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not es_admin():
    # Relanzar con permisos de administrador
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()
    
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from modulos.main_window.main_window import MainWindow
from modulos.login.login import PantallaLogin
from auxiliar.rutas import recurso_path
from PyQt5.QtWidgets import QApplication, QMessageBox
from acceso_db.utilidades import obtener_hora_servidor, sincronizar_hora_windows


class ControladorApp:
    def __init__(self, app):
        self.app = app
        self.login_window = None
        self.main_window = None

    def mostrar_login(self):
        self.login_window = PantallaLogin()
        self.login_window.accepted.connect(self._login_aceptado)
        self.login_window.show()

    def _login_aceptado(self):
        datos_usuario = self.login_window.usuario_datos
        self.login_window.close()
        self.mostrar_main(datos_usuario)

    def mostrar_main(self, datos_usuario):
        self.main_window = MainWindow(datos_usuario)
        self.main_window.logout_signal.connect(self._cerrar_sesion)
        self.main_window.show()

    def _cerrar_sesion(self):
        self.main_window.close()
        self.mostrar_login()


if __name__ == "__main__":
    import logging
    try:
        logging.info("Creando QApplication")
        app = QApplication(sys.argv)

        TaskManager.instance()  # Inicializar TaskManager
        # Splash screen
        logging.info("Mostrando splash screen")
        splash = QSplashScreen(QPixmap(recurso_path("assets/spinner/logo-carga.png")))
        splash.showMessage("Cargando...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        splash.show()
        app.processEvents()

        # Sincronizar hora con servidor SQL
        logging.info("Sincronizando hora con servidor SQL")
        from datetime import datetime
        hora_servidor = obtener_hora_servidor()
        sincronizar_hora_windows(hora_servidor)
        
        # time.sleep(2) # Simular tiempo de carga

        controlador = ControladorApp(app)
        controlador.mostrar_login()
        splash.finish(controlador.login_window)

        logging.info("Iniciando loop de eventos de QApplication")
        sys.exit(app.exec_())
    
    except Exception as e:
        logging.critical("ERROR CRITICO EN MAIN", exc_info=True)
        QMessageBox.critical(
            None,
            "Error crítico",
            "La aplicación no pudo iniciarse.\n"
            "Se generó un archivo de log.\n\n"
            "Envíe el archivo de la carpeta 'logs'."
        )

        sys.exit(1)