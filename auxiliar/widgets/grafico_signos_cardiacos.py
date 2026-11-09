# auxiliar/widgets/grafico_signos_cardiacos.py

from PyQt5.QtCore import QSettings, QEvent, QTimer
from PyQt5.QtWidgets import QSizePolicy

from matplotlib.figure import Figure

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas
)

from matplotlib.dates import DateFormatter


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

        self.ax = self.figura.add_subplot(111)

        self.mostrar_sin_datos()

    # =========================================================
    # TEMA
    # =========================================================

    def _tema_actual(self):

        settings = QSettings(
            "ClinicaBanfield",
            "HistoriasClinicas"
        )

        return str(
            settings.value(
                "tema",
                "oscuro"
            )
        ).lower()

    def _colores_tema(self):

        if self._tema_actual() == "claro":

            return {
                "figura": "#FFFFFF",
                "ejes": "#FFFFFF",
                "texto": "#202020",
                "grilla": "#D0D0D0",
                "borde": "#707070",
            }

        return {
            "figura": "#121212",
            "ejes": "#181818",
            "texto": "#EAEAEA",
            "grilla": "#555555",
            "borde": "#888888",
        }

    def _aplicar_tema(self):

        colores = self._colores_tema()

        # Fondo general
        self.figura.patch.set_facecolor(
            colores["figura"]
        )

        # Fondo del gráfico
        self.ax.set_facecolor(
            colores["ejes"]
        )

        # Ejes y números
        self.ax.tick_params(
            axis="both",
            colors=colores["texto"]
        )

        self.ax.xaxis.label.set_color(
            colores["texto"]
        )

        self.ax.yaxis.label.set_color(
            colores["texto"]
        )

        # Bordes
        for borde in self.ax.spines.values():

            borde.set_color(
                colores["borde"]
            )

        # Textos sueltos
        for texto in self.ax.texts:

            texto.set_color(
                colores["texto"]
            )

        # Leyenda
        leyenda = self.ax.get_legend()

        if leyenda:

            for texto in leyenda.get_texts():

                texto.set_color(
                    colores["texto"]
                )

            marco = leyenda.get_frame()

            marco.set_facecolor(
                colores["ejes"]
            )

            marco.set_edgecolor(
                colores["borde"]
            )

        self.draw_idle()

    def changeEvent(self, event):

        super().changeEvent(event)

        if event.type() in (
            QEvent.StyleChange,
            QEvent.PaletteChange
        ):
            # Se ejecuta después de que MainWindow
            # haya actualizado QSettings.
            QTimer.singleShot(
                0,
                self._aplicar_tema
            )

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

        self._aplicar_tema()

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

        colores = self._colores_tema()

        self.ax.grid(
            True,
            alpha=0.35,
            color=colores["grilla"]
        )

        # Leyenda arriba y fuera de las curvas
        self.ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=3,
            frameon=False
        )

        # -----------------------------------------------------
        # FECHAS
        # -----------------------------------------------------

        self.ax.xaxis.set_major_formatter(
            DateFormatter(
                "%d/%m/%Y\n%H:%M"
            )
        )

        self.figura.autofmt_xdate()

        # Reservar espacio para la leyenda
        self.figura.tight_layout(
            rect=[0, 0, 1, 0.90]
        )

        self._aplicar_tema()