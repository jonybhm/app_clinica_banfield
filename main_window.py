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
from acceso_db.permisos_repo import tiene_permiso_admin
from modulos.admin_usuarios import AdminUsuarios
from modulos.pacientes import PantallaPacientes  


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
        self.pacientes = PantallaPacientes( 
            id_profesional=datos_usuario.get("CODMED") or 0,
            nombre_profesional=datos_usuario["APELLIDO"]
            )
        
        # Asignar ID profesional (se usa en historia_clinica)
        self.historia_clinica.id_profesional = datos_usuario.get("CODMED") or 0
        self.historia_clinica.nombre_profesional = datos_usuario["APELLIDO"]

        # Crear logo
        logo = QLabel()
        pixmap = QPixmap("assets/logo/logo.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # Stack de pantallas
        self.stack = QStackedWidget()
        self.stack.addWidget(self.inicio)            # índice 0
        self.stack.addWidget(self.historia_clinica)  # índice 1
        self.stack.addWidget(self.pacientes)          # índice 2

        # Botones de navegación
        self.btn_inicio = QPushButton("INICIO")
        self.btn_historia = QPushButton("HISTORIA CLÍNICA")
        self.btn_pacientes = QPushButton("PACIENTES")
        self.btn_inicio.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_historia.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_pacientes.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        # Mostrar boton para admins de sistema
        if tiene_permiso_admin(datos_usuario["CODIGO"]):
            self._agregar_admin_menu()

        # Layout horizontal con logo y botones
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(logo)
        nav_layout.addWidget(self.btn_inicio)
        nav_layout.addWidget(self.btn_historia)
        nav_layout.addWidget(self.btn_pacientes)

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
        self._aplicar_tema("assets/styles/estilo_oscuro.qss")


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
        
        #Temas
        temas_menu = archivo_menu.addMenu("Temas")        
        tema_oscuro_action = QAction("Oscuro", self)
        tema_oscuro_action.triggered.connect(self._aplicar_tema_oscuro)
        temas_menu.addAction(tema_oscuro_action)
        tema_claro_action = QAction("Claro", self)
        tema_claro_action.triggered.connect(self._aplicar_tema_claro)
        temas_menu.addAction(tema_claro_action)

        #Salir
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

    def _aplicar_tema(self, archivo):
        '''
        Esta funcion toma la hoja de estilos y la aplica a la ventana principal

        Returns
        -------
        None.

        '''
        try:
            with open(archivo, "r") as f:
                estilo = f.read()
                self.setStyleSheet(estilo)
        except FileNotFoundError:
            print(f"Archivo de estilos {archivo} no encontrado")
            
        
    def login_exitoso(self, datos_usuario):
        self.btn_inicio.setEnabled(True)
        self.btn_historia.setEnabled(True)

        self.historia_clinica.id_profesional = datos_usuario.CODIGOEMPLEADO
        self.stack.setCurrentIndex(1)
        
    
    def _aplicar_tema_oscuro(self):
        QApplication.setStyle("Fusion")
        self._aplicar_tema("assets/styles/estilo_oscuro.qss")

    def _aplicar_tema_claro(self):
        QApplication.setStyle("Fusion")
        self._aplicar_tema("assets/styles/estilo_claro.qss")
        
    def _agregar_admin_menu(self):
        admin_menu = self.menuBar().addMenu("Administración")
        admin_action = QAction("Usuarios", self)
        admin_action.triggered.connect(self._abrir_admin)
        admin_menu.addAction(admin_action)

    def _abrir_admin(self):
        self.admin_window = AdminUsuarios(self.historia_clinica.id_profesional, self)
        # self.admin_window.setWindowTitle("Administración de Usuarios")
        # self.admin_window.resize(900, 600)
        self.admin_window.show()