# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:42:13 2025

@author: Jonathan
"""


#modulos/dialogo_consulta.py
from PyQt5.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QMessageBox, QScrollArea
)
from datetime import datetime
from auxiliar.rtf_utiles import limpiar_evolucion
from acceso_db.repositorio_historia import (
    obtener_lista_diagnosticos,
    obtener_lista_motivos_consulta,
    obtener_lista_examenes_complementarios,
    obtener_lista_tratamientos,
    obtener_lista_derivaciones,
    marcar_turno_atendido
)
from auxiliar.widgets_personalizados import ComboBoxBuscador
from acceso_db.conexion import obtener_conexion
import os
from auxiliar.pdf_utiles import generar_pdf_historia
from modulos.dialogo_informes import DialogoInformes
from auxiliar.widgets.spinner import SpinnerDialog
from PyQt5.QtWidgets import QApplication


class DialogoConsulta(QDialog):
    def __init__(self, datos_paciente, historial, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Consulta / Ver Historia Clínica")
        self.resize(600, 500)

        self.datos_paciente = datos_paciente  # diccionario
        self.historial = historial            # lista de dicts

        tabs = QTabWidget()
        self.tab_consulta = QWidget()
        self.tab_evolucion = QWidget()

        tabs.addTab(self.tab_consulta, "Consulta")
        tabs.addTab(self.tab_evolucion, "Evolución")

        self._init_tab_consulta()
        self._init_tab_evolucion()

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        # Botones inferiores
        botones_layout = QHBoxLayout()
        boton_guardar = QPushButton("Grabar")
        boton_guardar.clicked.connect(self.confirmar_guardado)

        boton_salir = QPushButton("Salir")
        boton_salir.clicked.connect(self.reject)

        boton_imprimir = QPushButton("Imprimir Historial Clínico")
        boton_imprimir.clicked.connect(self.abrir_vista_previa)

        boton_informes = QPushButton("Ver Informes")
        boton_informes.clicked.connect(self.abrir_informes)

        botones_layout.addWidget(boton_guardar)
        botones_layout.addWidget(boton_imprimir)
        botones_layout.addWidget(boton_informes)
        botones_layout.addWidget(boton_salir)

        layout.addLayout(botones_layout)

        self.setLayout(layout)

    def _init_tab_consulta(self):
        layout = QVBoxLayout()

        datos = self.datos_paciente
        layout.addWidget(QLabel(f"Paciente: {datos['NOMBRE']}"))
        layout.addWidget(QLabel(f"Fecha: {datos.get('FECHA', '')}"))
        layout.addWidget(QLabel(f"Historia Clínica: {datos.get('HCLIN', '')}"))
        layout.addWidget(QLabel(f"Hora: {datos.get('HORA', '')}"))
        layout.addWidget(QLabel(f"Protocolo: {datos.get('PROTOCOLO', '')}"))
        layout.addWidget(QLabel(f"Edad: {datos.get('EDAD', '')}"))
        layout.addWidget(QLabel(f"Sexo: {datos.get('SEXO', '')}"))
        layout.addWidget(QLabel(f"Entidad: {datos.get('ENTIDAD', '')}"))
        layout.addWidget(QLabel(f"Profesional: {datos.get('PROFESIONAL', '')}"))

        # Historial
        layout.addWidget(QLabel("Historial del Paciente:"))

        historial_widget = QWidget()
        historial_layout = QVBoxLayout(historial_widget)
        
        for entrada in self.historial:
            fecha = entrada.get("FECHA", "")
            evolucion = entrada.get("EVOLUCION", "")
            profesional = entrada.get("PROFESIONAL", "")
            hora = entrada.get("HORA", "")
            protocolo = entrada.get("PROTOCOLO", "")

            evolucion_limpia = limpiar_evolucion(evolucion)

            texto = QTextEdit()
            texto.setReadOnly(True)
            texto.setPlainText(
                f"Profesional: {profesional}\n"
                f"Hora: {hora}\n"
                f"Protocolo: {protocolo}\n"
                f"{evolucion_limpia}"
            )
            texto.setFixedHeight(120)

            historial_layout.addWidget(QLabel(str(fecha)))
            historial_layout.addWidget(texto)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(historial_widget)
        scroll.setFixedHeight(300)  

        layout.addWidget(scroll)

        self.tab_consulta.setLayout(layout)

    def _init_tab_evolucion(self):
        layout = QVBoxLayout()
        self.cmb_motivo = ComboBoxBuscador()
        self.txt_evolucion = QTextEdit()
        self.txt_evolucion.setFixedHeight(100)
        self.cmb_diagnostico = ComboBoxBuscador() 
        self.cmb_tratamiento = ComboBoxBuscador()
        self.cmb_examenes = ComboBoxBuscador()
        self.cmb_derivacion = ComboBoxBuscador()

        # Cargar listas desde DB
        self.diagnosticos = obtener_lista_diagnosticos()
        self.examenes = obtener_lista_examenes_complementarios()
        self.motivos = obtener_lista_motivos_consulta()
        self.tratamientos = obtener_lista_tratamientos()
        self.derivacion = obtener_lista_derivaciones()

        # Convertir en listas con formato "desc (codigo)"
        diagnosticos_items = [""] + [f"{desc} ({cod})" for cod, desc in self.diagnosticos]
        examenes_items = [""] + [f"{desc} ({cod})" for cod, desc in self.examenes]
        motivos_items = [""] + [f"{desc} ({cod})" for cod, desc in self.motivos]
        tratamientos_items = [""] + [f"{desc} ({cod})" for cod, desc in self.tratamientos]
        derivacion_items = [""] + [f"{desc} ({cod})" for cod, desc in self.derivacion]

        # Cargar en ComboBox
        self.cmb_diagnostico.setItems(diagnosticos_items)
        self.cmb_examenes.setItems(examenes_items)
        self.cmb_motivo.setItems(motivos_items)
        self.cmb_tratamiento.setItems(tratamientos_items)
        self.cmb_derivacion.setItems(derivacion_items)

        layout.addWidget(QLabel("Motivo de Consulta:"))
        layout.addWidget(self.cmb_motivo)

        layout.addWidget(QLabel("Evolución:"))
        layout.addWidget(self.txt_evolucion)

        layout.addWidget(QLabel("Diagnóstico:"))
        layout.addWidget(self.cmb_diagnostico)

        layout.addWidget(QLabel("Exámenes Complementarios:"))
        layout.addWidget(self.cmb_examenes)

        layout.addWidget(QLabel("Tratamiento:"))
        layout.addWidget(self.cmb_tratamiento)

        layout.addWidget(QLabel("Derivación:"))
        layout.addWidget(self.cmb_derivacion)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setLayout(layout)
        scroll.setWidget(container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.tab_evolucion.setLayout(main_layout)

    def confirmar_guardado(self):
        reply = QMessageBox.question(
            self, "Confirmación", "¿Desea guardar esta evolución?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.guardar_evolucion()

    def guardar_evolucion(self):
        # Spinner
        spinner = SpinnerDialog("Guardando evolución...")
        spinner.show()
        QApplication.processEvents()

        texto_diag = self.cmb_diagnostico.currentText()
        codigo_diag = None
        if "(" in texto_diag and texto_diag.endswith(")"):
            codigo_diag = texto_diag.split("(")[-1].rstrip(")")

        texto_final = self.txt_evolucion.toPlainText()

        conn = obtener_conexion()
        cursor = conn.cursor()

        # Datos base
        hclin = self.datos_paciente["HCLIN"]
        codpac = self.datos_paciente["CODPAC"]
        id_profesional = self.datos_paciente["ID_PROFESIONAL"]  
        fecha_actual = datetime.now().date()
        hora_actual = datetime.now().strftime("%H:%M")

        # Calcular SECUEN (máximo + 1 para este paciente)
        cursor.execute("SELECT ISNULL(MAX(SECUEN), 0) FROM dbo.AHISTCLIN WHERE CODPAC = ?", (codpac,))
        secuen = cursor.fetchone()[0] + 1

        # Calcular PROTOCOLO (máximo + 1 en toda la tabla)
        cursor.execute("SELECT ISNULL(MAX(PROTOCOLO), 0) FROM dbo.AHISTCLIN")
        protocolo = cursor.fetchone()[0] + 1

        # Insertar nueva evolución
        cursor.execute("""
            INSERT INTO dbo.AHISTCLIN (HCLIN, FECHA, SECUEN, PROFES, EVOLUCION, HORA, PROTOCOLO, CODPAC)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hclin,
            fecha_actual,
            secuen,
            id_profesional,
            texto_final,
            hora_actual,
            protocolo,
            codpac
        ))

        conn.commit()

        # Marcar el turno como atendido
        # marcar_turno_atendido(codpac, fecha_actual, id_profesional)

        conn.close()

        QMessageBox.information(self, "Éxito", "Evolución guardada correctamente")
        self.accept()  # Devuelve Accepted para que la tabla se actualice

    def abrir_vista_previa(self):
        spinner = SpinnerDialog("Abriendo vista previa...")
        spinner.show()
        QApplication.processEvents()

        archivo = generar_pdf_historia(self.datos_paciente, self.historial)       
        os.startfile(archivo)  

    def abrir_informes(self):
        spinner = SpinnerDialog("Abriendo informes...")
        spinner.show()
        QApplication.processEvents()

        codpac = self.datos_paciente["CODPAC"]
        dlg = DialogoInformes(codpac, self.datos_paciente["PROFESIONAL"], self)
        dlg.exec_()
