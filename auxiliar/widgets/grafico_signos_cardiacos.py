# auxiliar/widgets/grafico_signos_cardiacos.py

from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)

from matplotlib.dates import DateFormatter
from PyQt5.QtWidgets import QSizePolicy

class GraficoSignosCardiacos(FigureCanvas):

    def __init__(self, parent=None):

        self.figura = Figure(
            figsize=(8, 4)
        )

        super().__init__(
            self.figura
        )

        self.setParent(parent)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.setMinimumHeight(240)

        self.ax = (
            self.figura.add_subplot(111)
        )

        self.mostrar_sin_datos()

    # =========================================================
    # SIN DATOS
    # =========================================================

    def mostrar_sin_datos(self):

        self.ax.clear()

        self.ax.text(
            0.5,
            0.5,
            "No hay mediciones registradas",
            horizontalalignment="center",
            verticalalignment="center",
            transform=self.ax.transAxes
        )

        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.draw_idle()

    # =========================================================
    # ACTUALIZAR
    # =========================================================

    def actualizar(self, mediciones):

        self.ax.clear()

        if not mediciones:

            self.mostrar_sin_datos()
            return

        fechas = [
            m["FECHA_HORA"]
            for m in mediciones
        ]

        frecuencia = [
            m["FC"]
            for m in mediciones
        ]

        sistolica = [
            m["PAS"]
            for m in mediciones
        ]

        diastolica = [
            m["PAD"]
            for m in mediciones
        ]

        # -----------------------------------------------------
        # CURVAS
        # -----------------------------------------------------

        self.ax.plot(
            fechas,
            frecuencia,
            marker="o",
            label="Frecuencia cardíaca"
        )

        self.ax.plot(
            fechas,
            sistolica,
            marker="o",
            label="Presión sistólica"
        )

        self.ax.plot(
            fechas,
            diastolica,
            marker="o",
            label="Presión diastólica"
        )

        # -----------------------------------------------------
        # EJES
        # -----------------------------------------------------


        self.ax.set_xlabel(
            "Fecha"
        )

        self.ax.set_ylabel(
            "Valor (lpm / mmHg)"
        )

        self.ax.grid(
            True,
            alpha=0.3
        )

        self.ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=3,
            frameon=False
        )
        
        self.ax.xaxis.set_major_formatter(
            DateFormatter(
                "%d/%m/%Y\n%H:%M"
            )
        )

        self.figura.autofmt_xdate()

        self.figura.tight_layout(
            rect=[0, 0, 1, 0.90]
        )
        
        self.draw_idle()