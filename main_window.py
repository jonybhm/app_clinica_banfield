# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:24:11 2025

@author: Jonathan
"""
#main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QStackedWidget, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QApplication, QMenuBar, QMenu, QAction, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSettings
from modulos.inicio import PantallaInicio
from modulos.historia_clinica import PantallaHistoriaClinica
from modulos.login import PantallaLogin
from acceso_db.permisos_repo import tiene_permiso_admin
from modulos.admin_usuarios import AdminUsuarios
from modulos.pacientes import PantallaPacientes  
from PyQt5.QtCore import pyqtSignal
from auxiliar.widgets.spinner import SpinnerDialog
from PyQt5.QtWidgets import QApplication
from auxiliar.rutas import recurso_path

class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()

    '''
    Clase que representa la ventana principal
    Hereda propiedades de PyQT (Main Window)    
    '''
    def __init__(self, datos_usuario):  
        super().__init__()
        self.datos_usuario = datos_usuario
        
        self.settings = QSettings("ClinicaBanfield", "HistoriasClinicas")
        self.setWindowTitle("Clínica Banfield")
        self.setGeometry(200, 100, 900, 700)


        # Crear logo
        logo = QLabel()
        pixmap = QPixmap(recurso_path("assets/logo/logo.png")).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # Botones principales con imágenes
        btn_historia = QPushButton("Turnos y Agendas")
        btn_historia.setIcon(QIcon(recurso_path("assets/icons/historia.png")))
        btn_historia.setIconSize(pixmap.size())
        btn_historia.setFixedSize(250, 120)
        btn_historia.clicked.connect(self.abrir_historia_clinica)

        btn_pacientes = QPushButton("Pacientes")
        btn_pacientes.setIcon(QIcon(recurso_path("assets/icons/pacientes.png")))
        btn_pacientes.setIconSize(pixmap.size())
        btn_pacientes.setFixedSize(250, 120)
        btn_pacientes.clicked.connect(self.abrir_pacientes)

        btn_informes = QPushButton("Informes")
        btn_informes.setIcon(QIcon(recurso_path("assets/icons/informes.png")))
        btn_informes.setIconSize(pixmap.size())
        btn_informes.setFixedSize(250, 120)
        btn_informes.clicked.connect(self.abrir_informes)

        # Layout central
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        botones_layout.addWidget(btn_historia)
        botones_layout.addSpacing(40)
        botones_layout.addWidget(btn_pacientes)
        botones_layout.addSpacing(40)
        botones_layout.addWidget(btn_informes)
        botones_layout.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(logo)
        layout.addSpacing(40)
        layout.addLayout(botones_layout)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Barra de menú
        self._crear_menu()

        # Status bar
        tipo_usuario = "Médico" if datos_usuario["NIVEL"] == 5 else "Recepción"
        self.statusBar().showMessage(f"Usuario: {datos_usuario['APELLIDO']} | Puesto: {tipo_usuario}")  

        # Aplicar el último tema usado o el oscuro si no hay nada guardado
        tema_guardado = self.settings.value("tema", "oscuro")  
        if tema_guardado == "oscuro":
            self._aplicar_tema_oscuro()
        else:
            self._aplicar_tema_claro()

        self.showMaximized()


    def _crear_menu(self):
        # Mostrar spinner 
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()
        
        menubar = self.menuBar()
        archivo_menu = menubar.addMenu("Archivo")

        temas_menu = archivo_menu.addMenu("Temas")
        tema_oscuro_action = QAction("Oscuro", self)
        tema_oscuro_action.triggered.connect(self._aplicar_tema_oscuro)
        temas_menu.addAction(tema_oscuro_action)
        tema_claro_action = QAction("Claro", self)
        tema_claro_action.triggered.connect(self._aplicar_tema_claro)
        temas_menu.addAction(tema_claro_action)

        # Cambiar de usuario 
        cambiar_usuario_action = QAction("Cambiar de usuario", self)
        cambiar_usuario_action.triggered.connect(self._cambiar_usuario)
        archivo_menu.addAction(cambiar_usuario_action)

        # Opción salir
        salir_action = QAction("Salir", self)
        salir_action.triggered.connect(self.close)
        archivo_menu.addAction(salir_action)

        ayuda_menu = menubar.addMenu("Ayuda")
        acerca_action = QAction("Acerca de", self)
        acerca_action.triggered.connect(self._mostrar_acerca)
        ayuda_menu.addAction(acerca_action)

        if tiene_permiso_admin(self.datos_usuario["CODIGO"]):
            self._agregar_admin_menu()

    def _cambiar_usuario(self):
        """
        Emitir señal para cerrar sesión y volver al login.
        """
        self.logout_signal.emit()


    def _agregar_admin_menu(self):
        admin_menu = self.menuBar().addMenu("Administración")
        admin_action = QAction("Usuarios", self)
        admin_action.triggered.connect(self._abrir_admin)
        admin_menu.addAction(admin_action)

    def _abrir_admin(self):
        # Mostrar spinner
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()

        codmed = self.datos_usuario.get("CODMED") or 0
        self.admin_window = AdminUsuarios(codmed, self)
        self.admin_window.show()
        
    def _mostrar_acerca(self):
        '''
        Esta funcion ejecuta el boton "Acerca de"
        '''
        QMessageBox.information(
            self,
            "Acerca de",
            "Sistema de gestión de Historias Clínicas\n\n"
            "📌 Funcionalidades:\n"
            "- Turnos y Agendas: buscar turnos por fecha y gestionar evoluciones.\n"
            "- Informes: buscar informes de pacientes e imprimrlos.\n"
            "- Historias Clínicas: buscar e imprimir historial paciente.\n"
            "- Pacientes: buscar historias clínicas por nombre o DNI.\n\n"
            "Versión 1.0 - Clínica Banfield.\n"
            "Autor: Jonathan De Castro"
        )

    def _aplicar_tema(self, archivo):
        '''
        Esta funcion toma la hoja de estilos y la aplica a la ventana principal

        Returns
        -------
        None.

        '''
        # Mostrar spinner 
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()

        try:
            with open(archivo, "r") as f:
                estilo = f.read()
                QApplication.instance().setStyleSheet(estilo)  # aplica el estilo globalmente
            # Guardar la preferencia del usuario
            tema = "oscuro" if "oscuro" in archivo else "claro"
            self.settings.setValue("tema", tema)
        except FileNotFoundError:
            print(f"Archivo de estilos {archivo} no encontrado")
            
    def _aplicar_tema_oscuro(self):
        QApplication.setStyle("Fusion")
        self._aplicar_tema(recurso_path("assets/styles/estilo_oscuro.qss"))

    def _aplicar_tema_claro(self):
        QApplication.setStyle("Fusion")
        self._aplicar_tema(recurso_path("assets/styles/estilo_claro.qss"))
        
    def login_exitoso(self, datos_usuario):
        self.btn_inicio.setEnabled(True)
        self.btn_historia.setEnabled(True)

        self.historia_clinica.id_profesional = datos_usuario.CODIGOEMPLEADO
        self.stack.setCurrentIndex(1)
        
    
    def abrir_informes(self):
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()

        self.informes_window = InformesWindow(self.datos_usuario)
        self.informes_window.show()
   
    def abrir_historia_clinica(self):
        # Mostrar spinner 
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()

        self.historia_window = HistoriaClinicaWindow(self.datos_usuario)
        self.historia_window.show()

    def abrir_pacientes(self):
        # Mostrar spinner 
        spinner = SpinnerDialog("Cargando...")
        spinner.show()
        QApplication.processEvents()

        self.pacientes_window = PacientesWindow(self.datos_usuario)
        self.pacientes_window.show()


# Ventana secundaria para Historia Clínica

class HistoriaClinicaWindow(QMainWindow):
    def __init__(self, datos_usuario):
        super().__init__()
        self.setWindowTitle("Historia Clínica")
        # self.setGeometry(250, 150, 900, 600)
        self.showMaximized()

        widget = PantallaHistoriaClinica()
        widget.id_profesional = datos_usuario.get("CODMED") or 0
        widget.nombre_profesional = datos_usuario["APELLIDO"]
        widget.buscar_turnos_ui()

        btn_volver = QPushButton("Volver al Menú Principal")
        btn_volver.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(btn_volver)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        


# Ventana secundaria para Pacientes
class PacientesWindow(QMainWindow):
    def __init__(self, datos_usuario):
        super().__init__()
        self.setWindowTitle("Pacientes")
        # self.setGeometry(250, 150, 900, 600)
        self.showMaximized()

        widget = PantallaPacientes(
            id_profesional=datos_usuario.get("CODMED") or 0,
            nombre_profesional=datos_usuario["APELLIDO"]
        )

        btn_volver = QPushButton("Volver al Menú Principal")
        btn_volver.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(btn_volver)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

# Ventana secundaria para Informes
class InformesWindow(QMainWindow):
    def __init__(self, datos_usuario):
        super().__init__()
        self.setWindowTitle("Informes")
        self.showMaximized()

        from modulos.informes.pantalla_informes import PantallaInformes

        widget = PantallaInformes()

        btn_volver = QPushButton("Volver al Menú Principal")
        btn_volver.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.addWidget(btn_volver)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)