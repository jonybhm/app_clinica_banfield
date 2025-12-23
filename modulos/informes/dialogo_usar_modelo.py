# modulos/informes/dialogo_usar_modelo.py
import logging
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QLineEdit, QMessageBox
)

from acceso_db.conexion import obtener_conexion
from acceso_db.repositorio_historia import buscar_pacientes_triple_factor

from auxiliar.editor_texto.editor_richtext import EditorTextoEnriquecido
from auxiliar.editor_texto.editor_externo import editar_rtf_con_libreoffice
from auxiliar.editor_texto.rtf_preview import rtf_a_html_con_libreoffice
from auxiliar.threads.libreoffice_worker import LibreOfficeWorker

from modulos.dialogo_informes import DialogoInformes

log = logging.getLogger(__name__)


class DialogoUsarModelo(QDialog):
    def __init__(self, parent=None, datos_usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Informes de Pacientes")
        self.resize(1400, 800)

        # Habilitar minimizar / maximizar
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )

        self.datos_usuario = datos_usuario
        self.codpac_actual = None
        self.modelo_actual = None
        self.rtf_actual = None

        layout = QHBoxLayout(self)
        layout.setSpacing(20)

        # ---------------- Pacientes ----------------
        col_pac = QVBoxLayout()
        col_pac.addWidget(QLabel("Paciente"))

        self.pac_dni = QLineEdit()
        self.pac_dni.setPlaceholderText("DNI")
        self.pac_nombre = QLineEdit()
        self.pac_nombre.setPlaceholderText("Nombre")
        self.pac_apellido = QLineEdit()
        self.pac_apellido.setPlaceholderText("Apellido")

        btn_buscar_pac = QPushButton("Buscar")
        btn_buscar_pac.clicked.connect(self.buscar_paciente)

        self.lista_pacientes = QListWidget()
        self.lista_pacientes.itemClicked.connect(self.seleccionar_paciente)

        col_pac.addWidget(self.pac_dni)
        col_pac.addWidget(self.pac_nombre)
        col_pac.addWidget(self.pac_apellido)
        col_pac.addWidget(btn_buscar_pac)
        col_pac.addWidget(self.lista_pacientes)

        # ---------------- Modelos ----------------
        col_modelos = QVBoxLayout()
        col_modelos.addWidget(QLabel("Modelos"))

        self.buscar_modelo = QLineEdit()
        self.buscar_modelo.setPlaceholderText("🔍 Buscar modelo…")
        self.buscar_modelo.textChanged.connect(self.filtrar_modelos)

        self.lista_modelos = QListWidget()
        self.lista_modelos.itemClicked.connect(self.cargar_modelo)

        col_modelos.addWidget(self.buscar_modelo)
        col_modelos.addWidget(self.lista_modelos)

        # ---------------- Vista previa ----------------
        col_preview = QVBoxLayout()
        col_preview.addWidget(QLabel("Vista previa"))

        self.editor = EditorTextoEnriquecido()
        self.editor.setReadOnly(True)
        col_preview.addWidget(self.editor)

        # ---------------- Acciones ----------------
        col_acciones = QVBoxLayout()

        btn_editar = QPushButton("✏️ Editar informe")
        btn_guardar = QPushButton("💾 Guardar informe")
        btn_historial = QPushButton("📂 Informes anteriores")

        btn_editar.clicked.connect(self.editar_informe)
        btn_guardar.clicked.connect(self.guardar_informe)
        btn_historial.clicked.connect(self.ver_informes)

        for b in (btn_editar, btn_guardar, btn_historial):
            b.setFixedHeight(60)

        col_acciones.addStretch()
        col_acciones.addWidget(btn_editar)
        col_acciones.addWidget(btn_guardar)
        col_acciones.addWidget(btn_historial)
        col_acciones.addStretch()

        # ---------------- Layout final ----------------
        layout.addLayout(col_pac, 2)
        layout.addLayout(col_modelos, 2)
        layout.addLayout(col_preview, 4)
        layout.addLayout(col_acciones, 1)

        self.cargar_modelos()
        self.showMaximized()


    # ======================================================
    # Pacientes
    # ======================================================

    def buscar_paciente(self):
        self.lista_pacientes.clear()

        resultados = buscar_pacientes_triple_factor(
            dni=self.pac_dni.text(),
            nombre=self.pac_nombre.text(),
            apellido=self.pac_apellido.text()
        )

        for p in resultados:
            item = QListWidgetItem(f"{p['NOMBRE']} ({p['DOCUMENTO']})")
            item.setData(Qt.UserRole, p["CODPAC"])
            self.lista_pacientes.addItem(item)

    def seleccionar_paciente(self, item):
        self.codpac_actual = item.data(Qt.UserRole)

    # ======================================================
    # Modelos
    # ======================================================

    def cargar_modelos(self):
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT CODIGO, DESCRIPCION FROM dbo.TEXTOS ORDER BY DESCRIPCION")
        self.modelos = cur.fetchall()
        conn.close()

        self.refrescar_lista_modelos(self.modelos)

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
        codigo = item.data(Qt.UserRole)

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT CMEM FROM dbo.TEXTOS WHERE CODIGO = ?", (codigo,))
        self.rtf_actual = cur.fetchone()[0]
        conn.close()

        html = rtf_a_html_con_libreoffice(self.rtf_actual)
        self.editor.setHtml(html)

    # ======================================================
    # Acciones
    # ======================================================

    def editar_informe(self):
        if not self.rtf_actual:
            QMessageBox.warning(self, "Atención", "No hay informe cargado.")
            return

        self.worker = LibreOfficeWorker(
            editar_rtf_con_libreoffice,
            self.rtf_actual
        )
        self.worker.terminado.connect(self._editar_ok)
        self.worker.start()

    def _editar_ok(self, rtf):
        self.rtf_actual = rtf
        html = rtf_a_html_con_libreoffice(rtf)
        self.editor.setHtml(html)

    def guardar_informe(self):
        if not self.codpac_actual or not self.rtf_actual:
            QMessageBox.warning(self, "Atención", "Seleccione paciente y modelo.")
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
            self.rtf_actual,
            self.codpac_actual
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Informe guardado correctamente.")

    def ver_informes(self):
        if not self.codpac_actual:
            QMessageBox.warning(self, "Atención", "Seleccione un paciente.")
            return

        dlg = DialogoInformes(
            self.codpac_actual,
            self.datos_usuario["APELLIDO"],
            self
        )
        dlg.exec_()
