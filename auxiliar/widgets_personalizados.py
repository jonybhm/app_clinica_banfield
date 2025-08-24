# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 13:06:59 2025

@author: Jonathan
"""
#auxiliar/widgets_personalizados.py
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

class ComboBoxBuscador(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setMaxVisibleItems(10)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setFocusPolicy(Qt.StrongFocus)

        self._todos_los_items = []
        self.lineEdit().textEdited.connect(self._filtrar_items)

    def setItems(self, items):
        self._todos_los_items = items
        self.clear()
        self.addItems(items)

    def _filtrar_items(self, texto):
        texto = texto.strip().lower()
        self.clear()
        if texto:
            filtrados = [i for i in self._todos_los_items if texto in i.lower()]
        else:
            filtrados = self._todos_los_items
        self.addItems(filtrados)
        self.setEditText(texto)
