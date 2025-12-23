# modulos/informes/pantalla_informes.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from auxiliar.rutas import recurso_path

class PantallaInformes(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.setWindowTitle("Gestión de Informes")

        logo = QLabel()
        pixmap = QPixmap(recurso_path("assets/logo/logo.png")).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        btn_nuevo = QPushButton("Crear/Editar Modelo Informe")
        btn_nuevo.setIcon(QIcon(recurso_path("assets/icons/nuevo.png")))
        btn_nuevo.setIconSize(pixmap.size())
        btn_nuevo.setFixedSize(300, 120)

        btn_usar = QPushButton("Informes Pacientes")
        btn_usar.setIcon(QIcon(recurso_path("assets/icons/editar.png")))
        btn_usar.setIconSize(pixmap.size())
        btn_usar.setFixedSize(300, 120)

        btn_nuevo.clicked.connect(self.crear_modelo)
        btn_usar.clicked.connect(self.usar_modelo)

        layout.setAlignment(Qt.AlignHCenter)
        layout.addStretch()
        layout.addWidget(btn_nuevo, alignment=Qt.AlignHCenter)
        layout.addSpacing(20)
        layout.addWidget(btn_usar, alignment=Qt.AlignHCenter)
        layout.addStretch()

    def crear_modelo(self):
        from modulos.informes.dialogo_nuevo_modelo import DialogoNuevoModelo
        dlg = DialogoNuevoModelo(self)
        dlg.exec_()

    def usar_modelo(self):
        from modulos.informes.dialogo_usar_modelo import DialogoUsarModelo
        dlg = DialogoUsarModelo(self)
        dlg.exec_()