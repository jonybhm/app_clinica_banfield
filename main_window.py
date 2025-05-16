# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:24:11 2025

@author: Jonathan
"""

from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QStackedWidget, QLabel
from modulos.inicio import PantallaInicio
from modulos.historia_clinica import PantallaHistoriaClinica

class MainWindow(QMainWindow):    
    '''
    Clase que representa la ventana principal
    Hereda propiedades de PyQT (Main Window)    
    '''
    def __init__(self):
        super().__init__()
        
        #Titulo, Tamaño y Posicion de la ventana
        self.setWindowTitle("Clínica Banfield")
        self.setGeometry(100, 100, 800, 600)
        
        #Widget contenedor
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        #Layout en columna
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        #Botones de "INICIO" y "HISTORIA CLINICA"
        self.boton_inicio = QPushButton("INICIO")
        self.boton_historia = QPushButton("HISTORIA CLÍNICA")
        
        #Cambio de pantalla (Pantalla 0 y Pantalla 1)
        self.boton_inicio.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.boton_historia.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        #Agregar botones al UI
        layout.addWidget(self.boton_inicio)
        layout.addWidget(self.boton_historia)
        
        #Agregar stack al layout
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        #Agregar pantallas al stack
        self.stack.addWidget(PantallaInicio())
        self.stack.addWidget(PantallaHistoriaClinica())
        
        
        
        
        
            