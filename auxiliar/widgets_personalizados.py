# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 13:06:59 2025

@author: Jonathan
"""

from PyQt5.QtWidgets import QComboBox

class ComboBoxLimitado(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxVisibleItems(10)
