# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class PantallaInicio(QWidget):
    '''
    Clase que representa la pantalla de inicio
    Hereda propiedades de PyQT (Widgets)    
    '''
    def __init__(self):
        super().__init__()
        
        #Layout en columna y titulo 
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sistema Historia Clínica Banfield"))
        self.setLayout(layout)