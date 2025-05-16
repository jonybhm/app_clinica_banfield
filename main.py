# -*- coding: utf-8 -*-
"""
Created on Thu May 15 22:18:21 2025

@author: Jonathan
"""

import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    