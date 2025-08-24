# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 16:15:42 2025

@author: Jonathan
"""

# auxiliar/pdf_utiles.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os
from auxiliar.rtf_utiles import limpiar_evolucion


def generar_pdf_historia(datos_paciente, historial):
    """
    Genera un PDF con la historia clínica del paciente.
    datos_paciente: dict con info básica del paciente
    historial: lista de dicts con la evolución
    """
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    nombre_paciente = datos_paciente.get("NOMBRE", "Paciente desconocido")

    archivo = f"historia_{datos_paciente['CODPAC']}.pdf"
    doc = SimpleDocTemplate(
        archivo,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )

    estilos = getSampleStyleSheet()
    estilo_normal = estilos["Normal"]
    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceAfter=6,
    )
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        spaceAfter=4,
    )

    elementos = []

    # ==========================
    # ENCABEZADO
    # ==========================
    encabezado_tabla = Table(
        [[
            Paragraph("I.C.B.", estilo_titulo),
            Paragraph(f"Fecha: {fecha_actual}", estilo_normal)
        ]],
        colWidths=[300, 200]
    )
    encabezado_tabla.setStyle(TableStyle([
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(encabezado_tabla)

    # Nombre paciente
    elementos.append(Paragraph(f"Historia Clínica: {nombre_paciente}", estilo_titulo))
    elementos.append(Paragraph("=" * 90, estilo_normal))
    elementos.append(Spacer(1, 12))

    # ==========================
    # HISTORIAL
    # ==========================
    tabla_header = Table(
        [[
            "Fecha",
            "Profesional",
            "Hora Atención",
            "Protocolo"
        ]],
        colWidths=[100, 200, 100, 100]
    )
    tabla_header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla_header)
    elementos.append(Spacer(1, 6))

    for entrada in historial:
        fecha = entrada.get("FECHA", "")
        evolucion = entrada.get("EVOLUCION", "")
        evolucion_limpia = limpiar_evolucion(evolucion)

        profesional = entrada.get("PROFESIONAL", "")
        hora = entrada.get("HORA", "")
        protocolo = entrada.get("PROTOCOLO", "")

        # Cabecera de fila
        fila_tabla = Table(
            [[fecha, profesional, hora, protocolo]],
            colWidths=[100, 200, 100, 100]
        )
        fila_tabla.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elementos.append(fila_tabla)

        # Texto de evolución (multi-línea, alineado izquierda)
        if evolucion_limpia:
            elementos.append(Paragraph("Motivo de Consulta:", estilo_subtitulo))
            elementos.append(Paragraph(evolucion_limpia, estilo_normal))
            elementos.append(Spacer(1, 6))

    # ==========================
    # GENERAR PDF
    # ==========================
    doc.build(elementos)
    return os.path.abspath(archivo)
