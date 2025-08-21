# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 19:26:31 2025

@author: Jonathan
"""

# modulos/datos_usuario_widget.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QLabel,QTextEdit,QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate
from acceso_db.conexion import obtener_conexion

class DatosUsuarioWidget(QWidget):
    def __init__(self, codigo_usuario):
        super().__init__()
        self.codigo_usuario = codigo_usuario
        self.datos = None
        self.is_medico = False

        layout = QVBoxLayout(self)
        self.form = QFormLayout()
        layout.addLayout(self.form)

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        layout.addWidget(self.btn_guardar)

        self._cargar_datos_usuario()

    def _cargar_datos_usuario(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("SELECT NIVEL, APELLIDO FROM dbo.AUSUARIOS WHERE CODIGO=?", (self.codigo_usuario,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            self.form.addRow(QLabel("⚠ No se encontraron datos en AUSUARIOS"))
            return

        nivel, apellido = row
        self.is_medico = (nivel == 5)

        if self.is_medico:
            cursor.execute("SELECT * FROM dbo.AMEDEJEC WHERE USUHC=?", (self.codigo_usuario,))
            row = cursor.fetchone()
        else:
            cursor.execute("SELECT * FROM dbo.AEMPLEAD WHERE NOMBRE=?", (apellido,))
            row = cursor.fetchone()

        if not row:  # No encontró datos en la tabla destino
            conn.close()
            self.form.addRow(QLabel("⚠ No se encontraron datos adicionales para este usuario"))
            return

        # convertir tupla → dict {columna: valor}
        columnas = [c[0] for c in cursor.description]
        self.datos = {col: (val if val is not None else "") for col, val in zip(columnas, row)}

        conn.close()

        # Armar el formulario
        if self.is_medico:
            self._armar_formulario_medico()
        else:
            self._armar_formulario_empleado()


    def _armar_formulario_medico(self):
        self.inputs = {}

        form1 = QFormLayout()
        form2 = QFormLayout()

        # Columna 1
        self.inputs["NOMBRE"] = QLineEdit(str(self.datos.get("NOMBRE", "")))
        self.inputs["DIRECCION"] = QLineEdit(str(self.datos.get("DIRECCION", "")))
        self.inputs["EMAIL"] = QLineEdit(str(self.datos.get("EMAIL", "")))
        self.inputs["TELEFONO"] = QLineEdit(str(self.datos.get("TELEFONO", "")))
        self.inputs["CUIT"] = QLineEdit(str(self.datos.get("CUIT", "")))
        self.inputs["NROMATNAC"] = QLineEdit(str(self.datos.get("NROMATNAC", "")))
        self.fecha_alta = QLabel(str(self.datos.get("FECHALTA", "")))

        form1.addRow("Apellido y Nombre", self.inputs["NOMBRE"])
        form1.addRow("Dirección", self.inputs["DIRECCION"])
        form1.addRow("E-mail", self.inputs["EMAIL"])
        form1.addRow("Teléfonos", self.inputs["TELEFONO"])
        form1.addRow("CUIT", self.inputs["CUIT"])
        form1.addRow("Mat. Nacional", self.inputs["NROMATNAC"])
        form1.addRow("Fecha de Alta", self.fecha_alta)

        # Columna 2
        self.inputs["TELCELULAR"] = QLineEdit(str(self.datos.get("TELCELULAR", "")))
        self.inputs["NROMAT"] = QLineEdit(str(self.datos.get("NROMAT", "")))
        self.fecha_baja = QLabel(str(self.datos.get("FECHABAJA", "")))

        self.inputs["FENAC"] = QDateEdit()
        fenac = self.datos.get("FENAC")
        if fenac and hasattr(fenac, "year"):  # si es datetime válido
            self.inputs["FENAC"].setDate(QDate(fenac.year, fenac.month, fenac.day))
        self.inputs["FENAC"].setCalendarPopup(True)

        form2.addRow("Tel. Celular", self.inputs["TELCELULAR"])
        form2.addRow("Mat. Provincial", self.inputs["NROMAT"])
        form2.addRow("Fecha de Baja", self.fecha_baja)
        form2.addRow("Fecha de Nacimiento", self.inputs["FENAC"])

        # Síntesis Curricular
        self.inputs["CURRICULUM"] = QTextEdit(str(self.datos.get("CURRICULUM", "")))
        form1.addRow("Síntesis Curricular", self.inputs["CURRICULUM"])

        # Layout dos columnas
        cols = QHBoxLayout()
        cols.addLayout(form1)
        cols.addLayout(form2)

        self.form.addRow(cols)

    
    def _armar_formulario_empleado(self):
        self.inputs = {}

        self.inputs["NOMBRE"] = QLineEdit(str(self.datos.get("NOMBRE", "")))
        self.form.addRow("Nombre y Apellido:", self.inputs["NOMBRE"])

        self.inputs["DIRECCION"] = QLineEdit(str(self.datos.get("DIRECCION", "")))
        self.form.addRow("Dirección:", self.inputs["DIRECCION"])

        self.inputs["LOCALIDAD"] = QLineEdit(str(self.datos.get("LOCALIDAD", "")))
        self.form.addRow("Localidad:", self.inputs["LOCALIDAD"])

        self.inputs["EMAIL"] = QLineEdit(str(self.datos.get("EMAIL", "")))
        self.form.addRow("E-mail:", self.inputs["EMAIL"])

        self.inputs["FENAC"] = QDateEdit()
        fenac = self.datos.get("FENAC")
        if fenac and hasattr(fenac, "year"):
            self.inputs["FENAC"].setDate(QDate(fenac.year, fenac.month, fenac.day))
        self.inputs["FENAC"].setCalendarPopup(True)
        self.form.addRow("Fecha de Nacimiento:", self.inputs["FENAC"])


    def guardar_cambios(self):
        # Confirmación
        reply = QMessageBox.question(
            self, "Confirmar Guardado",
            "¿Desea guardar los cambios?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return  # cancelar

        conn = obtener_conexion()
        cursor = conn.cursor()

        if self.is_medico:
            cursor.execute("""
                UPDATE dbo.AMEDEJEC
                SET NOMBRE=?, DIRECCION=?, EMAIL=?, FENAC=?, TELCELULAR=?, NROMAT=?, CURRICULUM=?
                WHERE USUHC=?
            """, (
                self.inputs["NOMBRE"].text(),
                self.inputs["DIRECCION"].text(),
                self.inputs["EMAIL"].text(),
                self.inputs["FENAC"].date().toPyDate() if self.inputs["FENAC"].date() else None,
                self.inputs["TELCELULAR"].text(),
                self.inputs["NROMAT"].text(),
                self.inputs["CURRICULUM"].toPlainText(),
                self.codigo_usuario
            ))
        else:
            cursor.execute("""
                UPDATE dbo.AEMPLEAD
                SET NOMBRE=?, DIRECCION=?, EMAIL=?, FENAC=?
                WHERE NOMBRE=?
            """, (
                self.inputs["NOMBRE"].text(),
                self.inputs["DIRECCION"].text(),
                self.inputs["EMAIL"].text(),
                self.inputs["FENAC"].date().toPyDate() if self.inputs["FENAC"].date() else None,
                self.datos["NOMBRE"]
            ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Éxito", "Cambios guardados correctamente")