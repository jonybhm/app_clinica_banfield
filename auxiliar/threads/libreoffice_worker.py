from PyQt5.QtCore import QThread, pyqtSignal
import logging

log = logging.getLogger(__name__)

class LibreOfficeWorker(QThread):
    terminado = pyqtSignal(str)     # rtf resultante
    cancelado = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, funcion, rtf_inicial=""):
        super().__init__()
        self.funcion = funcion
        self.rtf_inicial = rtf_inicial

    def run(self):
        try:
            rtf = self.funcion(self.rtf_inicial)

            if not rtf:
                self.cancelado.emit()
                return

            self.terminado.emit(rtf)

        except Exception as e:
            log.exception("Error en LibreOfficeWorker")
            self.error.emit(str(e))
