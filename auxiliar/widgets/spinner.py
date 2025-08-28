# auxiliar/widgets/spinner.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class SpinnerDialog(QDialog):
    def __init__(self, mensaje="Cargando..."):
        super().__init__()

        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label_spinner = QLabel(self)
        self.label_spinner.setAlignment(Qt.AlignCenter)
        self.label_spinner.setStyleSheet("background: transparent;")

        self.movie = QMovie("assets/spinner/spinner.gif")
        if not self.movie.isValid():
            self.label_spinner.setText("⏳") 
        else:
            self.label_spinner.setMovie(self.movie)
            self.movie.start()
   
        self.label_texto = QLabel(mensaje, self)
        self.label_texto.setAlignment(Qt.AlignCenter)
        self.label_texto.setStyleSheet("color: white; font-size: 14px;")

        layout.addWidget(self.label_spinner)
        layout.addWidget(self.label_texto)