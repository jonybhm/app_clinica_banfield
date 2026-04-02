# modulos/informes/dialogo_usar_modelo.py
import logging
from datetime import datetime
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox
)

from acceso_db.conexion import obtener_conexion
from auxiliar.editor_texto.editor_richtext import EditorTextoEnriquecido
from auxiliar.editor_texto.rtf_preview import rtf_a_html_con_libreoffice

from workers.informes.informes_previos_worker import InformesPreviosWorker
from modulos.informes.dialogo_informes import DialogoInformes
from workers.base.base_task import BaseTask
from workers.base.task_manager import TaskManager
from workers.pacientes.pacientes_worker import BuscarPacientesWorker 

log = logging.getLogger(__name__)


class DialogoUsarModelo(QDialog):
    def __init__(self, datos_usuario, parent=None):
        super().__init__(parent)
        self.datos_usuario = datos_usuario

        self.setWindowTitle("Informes de Pacientes")
        self.resize(1400, 800)

        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )

        self.codpac_actual = None
        self.modelo_actual = None
        self.rtf_actual = None

        # 🆕 modelos seleccionados
        self.modelos_seleccionados = []

        layout = QHBoxLayout(self)
        layout.setSpacing(20)

        # ================= PACIENTES =================
        col_pac = QVBoxLayout()
        col_pac.addWidget(QLabel("Paciente"))

        self.pac_dni = QLineEdit()
        self.pac_dni.setPlaceholderText("DNI")
        self.pac_nombre = QLineEdit()
        self.pac_nombre.setPlaceholderText("Nombre")
        self.pac_apellido = QLineEdit()
        self.pac_apellido.setPlaceholderText("Apellido")

        btn_buscar_pac = QPushButton("Buscar")
        btn_buscar_pac.setIcon(QIcon(":/assets/svg/search.svg"))
        btn_buscar_pac.clicked.connect(self.buscar_paciente)

        self.lista_pacientes = QListWidget()
        self.lista_pacientes.itemClicked.connect(self.seleccionar_paciente)

        col_pac.addWidget(self.pac_dni)
        col_pac.addWidget(self.pac_nombre)
        col_pac.addWidget(self.pac_apellido)
        col_pac.addWidget(btn_buscar_pac)
        col_pac.addWidget(self.lista_pacientes)

        # ================= MODELOS =================
        col_modelos = QVBoxLayout()
        col_modelos.addWidget(QLabel("Modelos"))

        self.buscar_modelo = QLineEdit()
        self.buscar_modelo.setPlaceholderText("Buscar modelo…")
        self.buscar_modelo.textChanged.connect(self.filtrar_modelos)

        self.lista_modelos = QListWidget()
        self.lista_modelos.itemClicked.connect(self.cargar_modelo)

        # 🆕 botones conjunto
        self.btn_agregar = QPushButton("➕ Agregar al conjunto")
        self.btn_agregar.clicked.connect(self.agregar_modelo)

        self.btn_quitar = QPushButton("❌ Quitar seleccionado")
        self.btn_quitar.clicked.connect(self.quitar_modelo)

        # 🆕 lista seleccionados
        self.lista_seleccionados = QListWidget()

        col_modelos.addWidget(self.buscar_modelo)
        col_modelos.addWidget(self.lista_modelos)
        col_modelos.addWidget(self.btn_agregar)
        col_modelos.addWidget(QLabel("Modelos seleccionados"))
        col_modelos.addWidget(self.lista_seleccionados)
        col_modelos.addWidget(self.btn_quitar)

        # ================= PREVIEW =================
        col_preview = QVBoxLayout()
        col_preview.addWidget(QLabel("Vista previa"))

        self.lbl_paciente = QLabel("PACIENTE SELECCIONADO: —")
        col_preview.addWidget(self.lbl_paciente)

        self.editor = EditorTextoEnriquecido()
        self.editor.setReadOnly(True)
        col_preview.addWidget(self.editor)

        # ================= ACCIONES =================
        col_acciones = QVBoxLayout()

        self.btn_editar = QPushButton("Editar informe paciente")
        self.btn_guardar = QPushButton("Guardar informe paciente")
        self.btn_historial = QPushButton("Historial informes paciente")

        self.btn_editar.clicked.connect(self.editar_informe)
        self.btn_guardar.clicked.connect(self.guardar_informe)
        self.btn_historial.clicked.connect(self.ver_informes)

        self.btn_editar.setEnabled(False)
        self.btn_guardar.setEnabled(False)

        for b in (self.btn_editar, self.btn_guardar, self.btn_historial):
            b.setFixedHeight(60)

        col_acciones.addStretch()
        col_acciones.addWidget(self.btn_editar)
        col_acciones.addWidget(self.btn_guardar)
        col_acciones.addWidget(self.btn_historial)
        col_acciones.addStretch()

        layout.addLayout(col_pac, 2)
        layout.addLayout(col_modelos, 2)
        layout.addLayout(col_preview, 4)
        layout.addLayout(col_acciones, 1)

        self.showMaximized()

    # ================= PACIENTES =================

    def buscar_paciente(self):
        task = BuscarPacientesWorker(
            self.pac_dni.text(),
            self.pac_nombre.text(),
            self.pac_apellido.text()
        )
        task.signals.finished.connect(self._mostrar_pacientes)
        TaskManager.instance().run(task, "Buscando pacientes...")

    def _mostrar_pacientes(self, resultados):
        self.lista_pacientes.clear()
        for p in resultados:
            item = QListWidgetItem(f"{p['NOMBRE']} ({p['DOCUMENTO']})")
            item.setData(Qt.UserRole, p["CODPAC"])
            self.lista_pacientes.addItem(item)

    def seleccionar_paciente(self, item):
        self.codpac_actual = item.data(Qt.UserRole)
        self.lbl_paciente.setText(f"PACIENTE: {item.text()}")
        self._actualizar_estado_botones()

    # ================= MODELOS =================

    def cargar_modelos(self):
        from workers.informes.modelos_worker import cargar_modelos
        task = BaseTask(cargar_modelos)
        task.signals.finished.connect(self._mostrar_modelos)
        TaskManager.instance().run(task)

    def _mostrar_modelos(self, modelos):
        self.modelos = modelos
        self.refrescar_lista_modelos(modelos)

    def filtrar_modelos(self, texto):
        texto = texto.lower()
        filtrados = [(c, d) for c, d in self.modelos if texto in d.lower()]
        self.refrescar_lista_modelos(filtrados)

    def refrescar_lista_modelos(self, modelos):
        self.lista_modelos.clear()
        for codigo, desc in modelos:
            item = QListWidgetItem(desc)
            item.setData(Qt.UserRole, codigo)
            self.lista_modelos.addItem(item)

    def cargar_modelo(self, item):
        self.modelo_actual = (item.data(Qt.UserRole), item.text())

        from workers.informes.vista_previa_worker import cargar_vista_previa
        task = BaseTask(cargar_vista_previa, self.modelo_actual[0])
        task.signals.finished.connect(self._modelo_cargado)
        TaskManager.instance().run(task)

    def _modelo_cargado(self, data):
        self.rtf_actual, html = data
        self.editor.setHtml(html)
        self._actualizar_estado_botones()

    # ================= CONJUNTO =================

    def agregar_modelo(self):
        if not self.modelo_actual:
            QMessageBox.warning(self, "Atención", "Seleccione un modelo.")
            return

        codigo, desc = self.modelo_actual

        if any(c == codigo for c, _ in self.modelos_seleccionados):
            return

        self.modelos_seleccionados.append((codigo, desc))

        item = QListWidgetItem(desc)
        item.setData(Qt.UserRole, codigo)
        self.lista_seleccionados.addItem(item)

        self.actualizar_preview()

    def quitar_modelo(self):
        row = self.lista_seleccionados.currentRow()
        if row >= 0:
            item = self.lista_seleccionados.takeItem(row)
            codigo = item.data(Qt.UserRole)
            self.modelos_seleccionados = [
                (c, d) for c, d in self.modelos_seleccionados if c != codigo
            ]

            self.actualizar_preview()

    # ================= RTF =================

    # def concatenar_rtfs(self, rtfs):
    #     if not rtfs:
    #         return None

    #     def extraer_contenido(rtf):
    #         """
    #         Extrae SOLO el contenido interno del RTF,
    #         eliminando header y llaves externas.
    #         """
    #         if not rtf:
    #             return ""

    #         rtf = rtf.strip()

    #         # Buscar inicio del contenido (después del header)
    #         inicio = rtf.find(r"\viewkind")
    #         if inicio == -1:
    #             inicio = rtf.find(r"\pard")

    #         if inicio != -1:
    #             rtf = rtf[inicio:]

    #         # sacar última llave
    #         if rtf.endswith("}"):
    #             rtf = rtf[:-1]

    #         return rtf.strip()

    #     # 👉 usar el primero como base REAL
    #     base = rtfs[0].strip()

    #     if not base.endswith("}"):
    #         return base  # fallback

    #     # sacar cierre final
    #     base = base[:-1]

    #     # 👉 concatenar contenidos
    #     for rtf in rtfs[1:]:
    #         contenido = extraer_contenido(rtf)

    #         base += r"\par\par\b ---------\b0\par\par"
    #         base += contenido

    #     # cerrar documento
    #     base += "}"

    #     return base
        
    def actualizar_preview(self):
        if not self.modelos_seleccionados:
            self.editor.clear()
            self.html_actual = None
            return

        from workers.informes.vista_previa_worker import cargar_vista_previa

        html_total = "<html><body>"

        for codigo, desc in self.modelos_seleccionados:
            _, html = cargar_vista_previa(codigo)

            html_total += f"<h1>{desc}</h1>"
            html_total += "<p></p>"
            html_total += html
            html_total += "<p>--------------------</p>"

        html_total += "</body></html>"

        self.html_actual = html_total
        self.editor.setHtml(html_total)

    # ================= ACCIONES =================

    def editar_informe(self):
        if not hasattr(self, "html_actual") or not self.html_actual:
            QMessageBox.warning(self, "Atención", "No hay contenido.")
            return

        from auxiliar.editor_texto.rtf_preview import html_a_rtf_con_libreoffice
        from workers.editor_rtf.libreoffice_tasks import editar_rtf_task

        try:
            # 🔥 convertir HTML → RTF
            rtf = html_a_rtf_con_libreoffice(self.html_actual)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error convirtiendo a RTF:\n{e}")
            return

        task = BaseTask(editar_rtf_task, rtf)
        task.signals.finished.connect(self._editar_ok)

        TaskManager.instance().run(task, "Abriendo LibreOffice...")
 
    def _editar_ok(self, rtf):
        if not rtf:
            QMessageBox.warning(self, "Atención", "No se detectaron cambios.")
            return

        self.rtf_editado = rtf
        self.rtf_actual = rtf

        from auxiliar.editor_texto.rtf_preview import rtf_a_html_con_libreoffice

        html = rtf_a_html_con_libreoffice(rtf)
        self.editor.setHtml(html)

    def guardar_informe(self):
        print("DEBUG guardar:", bool(self.rtf_editado), self.codpac_actual)


   
        if not self.codpac_actual:
            QMessageBox.warning(self, "Atención", "Seleccione un paciente.")
            return

        if not hasattr(self, "rtf_editado") or not self.rtf_editado:
            QMessageBox.warning(self, "Atención", "Debe editar el informe antes de guardar.")
            return

        conn = obtener_conexion()
        cur = conn.cursor()

        cur.execute("SELECT ISNULL(MAX(PROTOCOLO),0)+1 FROM dbo.AINFOR")
        protocolo = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO dbo.AINFOR
            (PROTOCOLO, FESTUDIO, TIPEA, CMEMO, CODPAC)
            VALUES (?, ?, ?, ?, ?)
        """, (
            protocolo,
            datetime.now(),
            self.datos_usuario["CODIGO"],
            self.rtf_editado,
            self.codpac_actual
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Informe guardado correctamente.")

    def ver_informes(self):
        if not self.codpac_actual:
            QMessageBox.warning(self, "Atención", "Seleccione un paciente.")
            return

        task = InformesPreviosWorker(self.codpac_actual)
        task.signals.finished.connect(self._mostrar_informes)
        TaskManager.instance().run(task)

    def _mostrar_informes(self, informes):
        if not informes:
            QMessageBox.information(self, "Sin informes", "No hay informes.")
            return

        dialogo = DialogoInformes(informes, self.datos_usuario["APELLIDO"], self)
        dialogo.exec_()

    # ================= UTIL =================

    def _actualizar_estado_botones(self):
        habilitar = self.codpac_actual is not None and self.rtf_actual is not None
        self.btn_guardar.setEnabled(habilitar)
        self.btn_editar.setEnabled(True)

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, "_cargado"):
            self._cargado = True
            self.cargar_modelos()