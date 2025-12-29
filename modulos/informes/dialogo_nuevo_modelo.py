# modulos/informes/dialogo_nuevo_modelo.py
import logging
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QMessageBox, QListWidget, QInputDialog, QLineEdit, QListWidgetItem, 
)
from acceso_db.conexion import obtener_conexion

from auxiliar.editor_texto.editor_externo import editar_rtf_con_libreoffice
from auxiliar.editor_texto.rtf_preview import rtf_a_html_con_libreoffice
from auxiliar.editor_texto.editor_richtext import EditorTextoEnriquecido
from auxiliar.threads.libreoffice_worker import LibreOfficeWorker


log = logging.getLogger(__name__)

class DialogoNuevoModelo(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modelos de informe")
        self.resize(1200, 750)

        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
        )

        self.codigo_actual = None

        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        col_lista = QVBoxLayout()

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar modelo...")
        self.buscador.textChanged.connect(self.filtrar_lista)

        self.lista = QListWidget()
        self.lista.itemClicked.connect(self.cargar)
        self.lista.setMinimumWidth(260)

        col_lista.addWidget(self.buscador)
        col_lista.addWidget(self.lista)

        col_botones = QVBoxLayout()

        btn_nuevo = QPushButton("Crear nuevo modelo")
        btn_nuevo.setIcon(QIcon(":/assets/svg/new.svg"))
        btn_nuevo.setIconSize(QSize(20, 20))
        btn_eliminar = QPushButton("Eliminar modelo")
        btn_eliminar.setIcon(QIcon(":/assets/svg/delete.svg"))
        btn_eliminar.setIconSize(QSize(20, 20))

        for b in (btn_nuevo, btn_eliminar):
            b.setFixedWidth(180)
            b.setFixedHeight(60)

        col_botones.addStretch()
        col_botones.addWidget(btn_nuevo)
        col_botones.addWidget(btn_eliminar)
        col_botones.addStretch()

        col_preview = QVBoxLayout()

        self.editor = EditorTextoEnriquecido()
        self.editor.setReadOnly(True)
        self.editor.setFrameStyle(0)
        self.editor.setAcceptRichText(True)
        self.editor.setUndoRedoEnabled(False)
        self.editor.setCursorWidth(0)

        col_preview.addWidget(self.editor)

        col_acciones = QVBoxLayout()

        btn_clonar = QPushButton("Clonar y Editar modelo")
        btn_clonar.setIcon(QIcon(":/assets/svg/clone.svg"))
        btn_clonar.setIconSize(QSize(20, 20))

        btn_modificar = QPushButton("Modificar modelo")
        btn_modificar.setIcon(QIcon(":/assets/svg/edit.svg"))
        btn_modificar.setIconSize(QSize(20, 20))

        btn_clonar.setFixedWidth(180)
        btn_modificar.setFixedWidth(180)
        btn_clonar.setFixedHeight(60)
        btn_modificar.setFixedHeight(60)

        col_acciones.addStretch()
        col_acciones.addWidget(btn_clonar)
        col_acciones.addWidget(btn_modificar)
        col_acciones.addStretch()

        layout.addLayout(col_lista, 2)
        layout.addLayout(col_botones, 1)
        layout.addLayout(col_preview, 4)
        layout.addLayout(col_acciones, 1)

        btn_clonar.clicked.connect(self.clonar_modelo)
        btn_eliminar.clicked.connect(self.eliminar)
        btn_modificar.clicked.connect(self.modificar)
        btn_nuevo.clicked.connect(self.guardar_como_nuevo)

        self.cargar_lista()
        self.showMaximized()

        self.overlay = QLabel("Editando documento...\nEspere por favor", self)
        self.overlay.setAlignment(Qt.AlignCenter)
        self.overlay.setStyleSheet("""
            background-color: rgba(0, 0, 0, 160);
            color: white;
            font-size: 18px;
            border-radius: 8px;
        """)
        self.overlay.hide()

        self.lista.doubleClicked.connect(self.cargar)


    def filtrar_lista(self, texto):
        texto = texto.lower()

        self.lista.clear()
        for codigo, desc in self.modelos:
            if texto in desc.lower():
                item = QListWidgetItem(desc)
                item.setData(Qt.UserRole, codigo)
                self.lista.addItem(item)

    def cargar_lista(self):
        try:
                conn = obtener_conexion()
                cur = conn.cursor()
                cur.execute("SELECT CODIGO, DESCRIPCION FROM dbo.TEXTOS ORDER BY DESCRIPCION")
                self.modelos = cur.fetchall()
                conn.close()

                self.lista.clear()
                for codigo, desc in self.modelos:
                    item = QListWidgetItem(desc)
                    item.setData(Qt.UserRole, codigo)
                    self.lista.addItem(item)
        except Exception:
            log.exception("Error cargando lista de modelos")
            QMessageBox.critical(self, "Error", "No se pudieron cargar los modelos")


    def cargar(self):
        item = self.lista.currentItem()
        if not item:
            return

        self.codigo_actual = item.data(Qt.UserRole)

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute(
            "SELECT CMEM FROM dbo.TEXTOS WHERE CODIGO = ?",
            (self.codigo_actual,)
        )
        row = cur.fetchone()
        conn.close()

        if not row or not row[0]:
            QMessageBox.warning(self, "Error", "No se pudo cargar el modelo.")
            return

        try:
            html = rtf_a_html_con_libreoffice(row[0])
            self.editor.clear()
            self.editor.setHtml(html)
        except Exception:
            log.exception("Error mostrando vista previa")
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo generar la vista previa."
            )


    def modificar(self):
        if not self.codigo_actual:
            QMessageBox.warning(self, "Atención", "No hay modelo cargado.")
            return

        confirmar = QMessageBox.question(
            self,
            "Confirmar",
            "¿Desea modificar este modelo?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmar != QMessageBox.Yes:
            return

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT CMEM FROM dbo.TEXTOS WHERE CODIGO = ?", (self.codigo_actual,))
        rtf_actual = cur.fetchone()[0]
        conn.close()


        self.worker = LibreOfficeWorker(
            editar_rtf_con_libreoffice,
            rtf_actual
        )

        self.worker.terminado.connect(self._modificar_guardar)
        self.worker.cancelado.connect(self._libreoffice_cancelado)
        self.worker.error.connect(self._libreoffice_error)

        self.bloquear_ui(True)
        self.worker.start()



    def guardar_como_nuevo(self):
        nombre, ok = QInputDialog.getText(self, "Nuevo modelo", "Nombre:")
        if not ok or not nombre.strip():
            return

        self.nombre_nuevo = nombre.strip()

        self.worker = LibreOfficeWorker(
            editar_rtf_con_libreoffice,
            ""
        )

        self.worker.terminado.connect(self._crear_guardar)
        self.worker.cancelado.connect(self._libreoffice_cancelado)
        self.worker.error.connect(self._libreoffice_error)

        self.bloquear_ui(True)
        self.worker.start()
            

    def eliminar(self):
        idx = self.lista.currentRow()
        if idx < 0:
            return

        codigo = self.modelos[idx][0]
        nombre = self.modelos[idx][1]

        confirmar = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el modelo:\n\n{nombre}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar != QMessageBox.Yes:
            return

        try:
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.TEXTOS WHERE CODIGO = ?", codigo)
            conn.commit()
            conn.close()

            self.editor.clear()
            self.codigo_actual = None
            self.cargar_lista()

            QMessageBox.information(self, "OK", "Modelo eliminado")

        except Exception as e:
            from auxiliar.debug.logger import log_error
            log.exception("Error al eliminar modelo", e)
            QMessageBox.critical(self, "Error", "No se pudo eliminar el modelo.\nVer log.")

   

    def clonar_modelo(self):
        if not self.codigo_actual:
            QMessageBox.warning(
                self,
                "Atención",
                "Debe seleccionar un modelo para usar como base."
            )
            return

        nombre, ok = QInputDialog.getText(
            self,
            "Nuevo modelo",
            "Nombre del nuevo modelo:"
        )
        if not ok or not nombre.strip():
            return

        self.nombre_nuevo = nombre.strip()


        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute(
            "SELECT CMEM FROM dbo.TEXTOS WHERE CODIGO = ?",
            (self.codigo_actual,)
        )
        rtf_base = cur.fetchone()[0]
        conn.close()


        self.worker = LibreOfficeWorker(
            editar_rtf_con_libreoffice,
            rtf_base
        )

        self.worker.terminado.connect(self._clonar_guardar)
        self.worker.cancelado.connect(self._libreoffice_cancelado)
        self.worker.error.connect(self._libreoffice_error)

        self.bloquear_ui(True)
        self.worker.start()


    def bloquear_ui(self, bloqueado: bool):
        self.setEnabled(not bloqueado)

        if bloqueado:
            self._mostrar_overlay("Editando documento…")
        else:
            self._ocultar_overlay()

    def _modificar_guardar(self, rtf_nuevo):
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute(
            "UPDATE dbo.TEXTOS SET CMEM = ? WHERE CODIGO = ?",
            (rtf_nuevo, self.codigo_actual)
        )
        conn.commit()
        conn.close()

        self.bloquear_ui(False)
        QMessageBox.information(self, "OK", "Modelo modificado correctamente")

    def _libreoffice_cancelado(self):
        self.bloquear_ui(False)
        QMessageBox.information(self, "Cancelado", "Edición cancelada por el usuario")

    def _libreoffice_error(self, msg):
        self.bloquear_ui(False)
        QMessageBox.critical(self, "Error", f"Error editando documento:\n{msg}")

    def _crear_guardar(self, rtf):
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT ISNULL(MAX(CODIGO),0)+1 FROM dbo.TEXTOS")
        codigo = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO dbo.TEXTOS (CODIGO, DESCRIPCION, CMEM)
            VALUES (?, ?, ?)
        """, (codigo, self.nombre_nuevo, rtf))

        conn.commit()
        conn.close()

        self.bloquear_ui(False)
        self.cargar_lista()

        QMessageBox.information(self, "OK", "Modelo creado correctamente")

    def _clonar_guardar(self, rtf_nuevo):
        try:
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT ISNULL(MAX(CODIGO),0)+1 FROM dbo.TEXTOS")
            nuevo_codigo = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO dbo.TEXTOS (CODIGO, DESCRIPCION, CMEM)
                VALUES (?, ?, ?)
            """, (nuevo_codigo, self.nombre_nuevo, rtf_nuevo))

            conn.commit()
            conn.close()

            self.cargar_lista()
            QMessageBox.information(self, "OK", "Modelo clonado correctamente")

        finally:
            self.bloquear_ui(False)

    def _mostrar_overlay(self, texto):
        self.overlay.setText(texto)
        self.overlay.setGeometry(self.rect())
        self.overlay.raise_()
        self.overlay.show()

    def _ocultar_overlay(self):
        self.overlay.hide()