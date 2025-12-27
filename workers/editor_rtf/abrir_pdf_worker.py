# auxiliar/workers/abrir_pdf_worker.py
from workers.base.base_task import BaseTask
from auxiliar.pdf_utiles import generar_pdf_historia
import os

class AbrirPdfWorker(BaseTask):
    def __init__(self, datos, historial):
        self.datos = datos
        self.historial = historial
        super().__init__(self._run)

    def _run(self):
        archivo = generar_pdf_historia(self.datos, self.historial)
        os.startfile(archivo)
