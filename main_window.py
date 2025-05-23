# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:24:11 2025

@author: Jonathan
"""

from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QStackedWidget, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QApplication, QMenuBar, QMenu, QAction, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from modulos.inicio import PantallaInicio
from modulos.historia_clinica import PantallaHistoriaClinica
from modulos.login import PantallaLogin

class MainWindow(QMainWindow):    
    '''
    Clase que representa la ventana principal
    Hereda propiedades de PyQT (Main Window)    
    '''
    def __init__(self, datos_usuario):  # ← RECIBE los datos de usuario
        super().__init__()

        self.setWindowTitle("Clínica Banfield")
        self.setGeometry(100, 100, 800, 600)

        # Inicializar pantallas
        self.inicio = PantallaInicio()
        self.historia_clinica = PantallaHistoriaClinica()

        # Asignar ID profesional (se usa en historia_clinica)
        self.historia_clinica.id_profesional = datos_usuario["CODIGO"]

        # Crear logo
        logo = QLabel()
        pixmap = QPixmap("assets/logo/logo.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # Stack de pantallas
        self.stack = QStackedWidget()
        self.stack.addWidget(self.inicio)            # índice 0
        self.stack.addWidget(self.historia_clinica)  # índice 1

        # Botones de navegación
        self.btn_inicio = QPushButton("INICIO")
        self.btn_historia = QPushButton("HISTORIA CLÍNICA")
        self.btn_inicio.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_historia.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        # Layout horizontal con logo y botones
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(logo)
        nav_layout.addWidget(self.btn_inicio)
        nav_layout.addWidget(self.btn_historia)

        # Layout vertical principal
        layout = QVBoxLayout()
        layout.addLayout(nav_layout)
        layout.addWidget(self.stack)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Crear barra de menú
        self._crear_menu()

        # Mostrar tipo de usuario en consola
        tipo_usuario = "Médico" if datos_usuario["NIVEL"] == 5 else "Recepción"
        self.statusBar().showMessage(f"Usuario: {datos_usuario['APELLIDO']} | Puesto: {tipo_usuario}")

        # Aplicar tema oscuro
        QApplication.setStyle("Fusion")
        self._aplicar_tema_oscuro()
        
        
        
        
    def _crear_menu(self):
        '''
        Esta funcion crea una barra de menu

        Returns
        -------
        None.

        '''
        menubar = self.menuBar()
        
        #Menu Archivo
        archivo_menu = menubar.addMenu("Archivo")
        salir_action = QAction("Salir", self)
        salir_action.triggered.connect(self.close)
        archivo_menu.addAction(salir_action)
        
        #Menu Ayuda
        ayuda_menu = menubar.addMenu("Ayuda")
        acerca_action = QAction("Acerca de", self)
        acerca_action.triggered.connect(self._mostrar_acerca)
        ayuda_menu.addAction(acerca_action)
        
    def _mostrar_acerca(self):
        '''
        Esta funcion ejecuta el boton "Acerca de"
        '''
        QMessageBox.Information(self, "Acerca de", "Sistema de gestión Historias Clínicas")
        
    def _aplicar_tema_oscuro(self):
        '''
        Esta funcion toma la hoja de estilos y la aplica a la ventana principal

        Returns
        -------
        None.

        '''
        try:
            with open("assets/styles/estilo_oscuro.qss", "r") as f:
                estilo = f.read()
                self.setStyleSheet(estilo)
        except FileNotFoundError:
            print("Archivo de estilos no encontrado")
            
        
    def login_exitoso(self, datos_usuario):
        self.btn_inicio.setEnabled(True)
        self.btn_historia.setEnabled(True)

        self.historia_clinica.id_profesional = datos_usuario.CODIGOEMPLEADO
        self.stack.setCurrentIndex(1)
        
        
        
            