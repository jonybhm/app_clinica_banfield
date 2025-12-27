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
from acceso_db.repositorio_historia import buscar_pacientes_triple_factor

from auxiliar.editor_texto.editor_richtext import EditorTextoEnriquecido
from auxiliar.editor_texto.editor_externo import editar_rtf_con_libreoffice
from auxiliar.editor_texto.rtf_preview import rtf_a_html_con_libreoffice
from auxiliar.threads.libreoffice_worker import LibreOfficeWorker

from workers.informes.informes_previos_worker import InformesPreviosWorker
from modulos.informes.dialogo_informes import DialogoInformes
from workers.base.base_task import BaseTask
from workers.base.task_manager import TaskManager
from workers.pacientes.pacientes_worker import buscar_pacientes_task 

log = logging.getLogger(__name__)


class DialogoUsarModelo(QDialog):
    def __init__(self, datos_usuario, parent=None):
        super().__init__(parent)
        self.datos_usuario = datos_usuario
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

        # Pacientes
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
        btn_buscar_pac.setIconSize(QSize(20, 20))
        btn_buscar_pac.clicked.connect(self.buscar_paciente)

        self.lista_pacientes = QListWidget()
        self.lista_pacientes.itemClicked.connect(self.seleccionar_paciente)

        col_pac.addWidget(self.pac_dni)
        col_pac.addWidget(self.pac_nombre)
        col_pac.addWidget(self.pac_apellido)
        col_pac.addWidget(btn_buscar_pac)
        col_pac.addWidget(self.lista_pacientes)

        # Modelos
        col_modelos = QVBoxLayout()
        col_modelos.addWidget(QLabel("Modelos"))

        self.buscar_modelo = QLineEdit()
        self.buscar_modelo.setPlaceholderText("Buscar modelo…")
        self.buscar_modelo.textChanged.connect(self.filtrar_modelos)

        self.lista_modelos = QListWidget()
        self.lista_modelos.itemClicked.connect(self.cargar_modelo)

        col_modelos.addWidget(self.buscar_modelo)
        col_modelos.addWidget(self.lista_modelos)

        # Vista previa
        col_preview = QVBoxLayout()
        col_preview.addWidget(QLabel("Vista previa"))

        self.lbl_paciente = QLabel("PACIENTE SELECCIONADO: —")
        self.lbl_paciente.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                padding: 6px;
                background: #ecf0f1;
                border-radius: 4px;
            }
        """)
        col_preview.addWidget(self.lbl_paciente)
        
        self.editor = EditorTextoEnriquecido()
        self.editor.setReadOnly(True)
        col_preview.addWidget(self.editor)

        # Acciones
        col_acciones = QVBoxLayout()

        self.btn_editar = QPushButton("Editar informe")
        self.btn_editar.setIcon(QIcon(":/assets/svg/inform.svg"))
        self.btn_editar.setIconSize(QSize(20, 20))
        self.btn_guardar = QPushButton("Guardar informe")
        self.btn_guardar.setIcon(QIcon(":/assets/svg/save.svg"))
        self.btn_guardar.setIconSize(QSize(20, 20))
        self.btn_historial = QPushButton("Informes anteriores")
        self.btn_historial.setIcon(QIcon(":/assets/svg/folder.svg"))
        self.btn_historial.setIconSize(QSize(20, 20))

        self.btn_editar.setEnabled(False)
        self.btn_guardar.setEnabled(False)
        
        self.btn_editar.clicked.connect(self.editar_informe)
        self.btn_guardar.clicked.connect(self.guardar_informe)
        self.btn_historial.clicked.connect(self.ver_informes)

        for b in (self.btn_editar, self.btn_guardar, self.btn_historial):
            b.setFixedHeight(60)

        col_acciones.addStretch()
        col_acciones.addWidget(self.btn_editar)
        col_acciones.addWidget(self.btn_guardar)
        col_acciones.addWidget(self.btn_historial)
        col_acciones.addStretch()

        # Layout final
        layout.addLayout(col_pac, 2)
        layout.addLayout(col_modelos, 2)
        layout.addLayout(col_preview, 4)
        layout.addLayout(col_acciones, 1)

        self.showMaximized()



    # Pacientes


    def buscar_paciente(self):
        task = BaseTask(
            buscar_pacientes_task,
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
        self.paciente_nombre = item.text()
        self.lbl_paciente.setText(f"PACIENTE SELECCIONADO: {self.paciente_nombre}")
        self._actualizar_estado_botones()

        self.btn_guardar.setEnabled(True)
        self.btn_editar.setEnabled(True)
        self.btn_historial.setEnabled(True)



    # Modelos


    def cargar_modelos(self):
        from workers.informes.modelos_worker import cargar_modelos

        task = BaseTask(cargar_modelos)
        task.signals.finished.connect(self._mostrar_modelos)
        TaskManager.instance().run(task, "Cargando modelos...")

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
        codigo = item.data(Qt.UserRole)

        from workers.informes.vista_previa_worker import cargar_vista_previa

        task = BaseTask(cargar_vista_previa, codigo)
        task.signals.finished.connect(self._modelo_cargado)
        TaskManager.instance().run(task, "Cargando modelo...")

    def _modelo_cargado(self, data):
        self.rtf_actual, html = data
        self.editor.setHtml(html)
        self._actualizar_estado_botones()

    # Acciones


    def editar_informe(self):
        if not self.rtf_actual:
            QMessageBox.warning(self, "Atención", "No hay informe cargado.")
            return

        from workers.editor_rtf.libreoffice_tasks import editar_rtf_task

        task = BaseTask(editar_rtf_task, self.rtf_actual)
        task.signals.finished.connect(self._editar_ok)
        TaskManager.instance().run(task, "Abriendo LibreOffice...")

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

        task = InformesPreviosWorker(self.codpac_actual)
        task.signals.finished.connect(self._mostrar_informes)
        task.signals.error.connect(self._error_informes)
        TaskManager.instance().run(task, "Cargando informes...")

    def _mostrar_informes(self, informes):
        try:
            print("📥 _mostrar_informes llamado")
            print("Tipo:", type(informes))
            print("Cantidad:", len(informes) if informes else "None")

            if not informes:
                QMessageBox.information(self, "Sin informes", "El paciente no tiene informes.")
                return

            dialogo = DialogoInformes(
                informes=informes,
                nombre_profesional=self.datos_usuario["APELLIDO"],
                parent=self
            )

            print("🟢 Abriendo diálogo...")
            dialogo.exec_()
            print("🟢 Diálogo cerrado")

        except Exception as e:
            import traceback
            print("❌ ERROR EN _mostrar_informes")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", str(e))
    
    def _error_informes(self, error):
      QMessageBox.critical(self, "Error al cargar informes", error)

        
    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, "_cargado"):
            self._cargado = True
            self.cargar_modelos()



    def _actualizar_estado_botones(self):
        habilitar = self.codpac_actual is not None and self.rtf_actual is not None
        self.btn_guardar.setEnabled(habilitar)
        self.btn_editar.setEnabled(habilitar)