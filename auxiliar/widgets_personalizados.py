# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 13:06:59 2025

@author: Jonathan
"""
#auxiliar/widgets_personalizados.py
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt
from datetime import datetime

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


def formatear_fecha(fecha):
    """Convierte '2020-04-15 00:00:00' → '15/04/2020'."""
    if not fecha:
        return ""

    # Si viene como datetime
    if isinstance(fecha, datetime):
        return fecha.strftime("%d/%m/%Y")

    # Si viene como string
    try:
        # Intenta parsear con hora al final
        dt = datetime.strptime(fecha[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y")
    except:
        try:
            # Intenta parsear solo fecha
            dt = datetime.strptime(fecha[:10], "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except:
            return fecha