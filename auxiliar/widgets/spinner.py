# auxiliar/widgets/spinner.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen

class Spinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(16)  # ~60fps
        self.setFixedSize(50, 50)

    def rotate(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.blue, 4)
        painter.setPen(pen)

        rect = self.rect().adjusted(6, 6, -6, -6)
        painter.drawArc(rect, self.angle * 16, 270 * 16)

class SpinnerDialog(QWidget):
    def __init__(self, texto="Cargando..."):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.spinner = Spinner()
        self.label = QLabel(texto)
        self.label.setStyleSheet("color: #4285F4; font-size: 14px;")

        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setFixedSize(150, 150)