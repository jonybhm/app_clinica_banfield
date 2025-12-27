# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 19:26:31 2025

@author: Jonathan
"""

# modulos/permisos_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QCheckBox, QPushButton
from acceso_db.conexion import obtener_conexion

class PermisosWidget(QWidget):
    def __init__(self, codigo_usuario):
        super().__init__()
        self.codigo_usuario = codigo_usuario
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "N. PROG.", "PROGRAMA", "ACCESO",
            "ALTA", "BAJA", "MODIF", "CONSULTA", "IMPRIME", "PERM. ESP."
        ])
        layout.addWidget(self.table)

        # Botón guardar
        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.clicked.connect(self.guardar_permisos)
        layout.addWidget(self.btn_guardar)

        self._cargar_permisos()

    def _cargar_permisos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.NUMPROG, p.DESCRIPCION, a.TIPOACC, a.ALTA, a.BAJA, a.MODIF, a.CONSULTA, a.IMPRIME, a.PERMESP
            FROM dbo.ADETER a
            INNER JOIN dbo.APGMSIS p ON a.NUMPROG = p.CODIGO
            WHERE a.CODIGO = ?
        """, (self.codigo_usuario,))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            numprog, desc, tipoacc, alta, baja, modif, consulta, imprime, permesp = row
            self.table.setItem(i, 0, QTableWidgetItem(str(numprog)))
            self.table.setItem(i, 1, QTableWidgetItem(desc))

            # Columna Acceso
            acceso = "DENEGADO"
            checks = [alta, baja, modif, consulta, imprime, permesp]
            if all(v == 1 for v in checks):
                acceso = "TOTAL"
            elif any(v == 1 for v in checks):
                acceso = "PARCIAL"

            self.table.setItem(i, 2, QTableWidgetItem(acceso))

            # Checkboxes
            for j, val in enumerate(checks, start=3):
                chk = QCheckBox()
                chk.setChecked(val == 1)
                self.table.setCellWidget(i, j, chk)

    def guardar_permisos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        for i in range(self.table.rowCount()):
            numprog = int(self.table.item(i, 0).text())
            values = []
            for j in range(3, 9):
                chk = self.table.cellWidget(i, j)
                values.append(1 if chk.isChecked() else 2)

            # Recalcular TIPOACC
            if all(v == 1 for v in values):
                tipoacc = 2
            elif any(v == 1 for v in values):
                tipoacc = 1
            else:
                tipoacc = 3

            cursor.execute("""
                UPDATE dbo.ADETER
                SET TIPOACC=?, ALTA=?, BAJA=?, MODIF=?, CONSULTA=?, IMPRIME=?, PERMESP=?
                WHERE CODIGO=? AND NUMPROG=?
            """, (tipoacc, *values, self.codigo_usuario, numprog))

        conn.commit()
        conn.close()
