# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 16:15:42 2025

@author: Jonathan
"""

import re

from striprtf.striprtf import rtf_to_text

def limpiar_evolucion(rtf):
    print("\n[DEBUG] RTF ORIGINAL:")
    print(rtf)
    try:
        texto_plano = rtf_to_text(rtf).strip()
        print("[DEBUG] TEXTO LIMPIO:")
        print(texto_plano)
        return texto_plano
    except Exception as e:
        print("[ERROR] Al convertir RTF:", e)
        return ""

def strip_rtf(rtf_text):
    """
    Convierte texto RTF a texto plano eliminando el formato.
    """
    if not rtf_text:
        return ""
    # Eliminar encabezados RTF básicos y códigos de formato
    clean = re.sub(r'\\[a-z]+\d* ?', '', rtf_text)   # elimina \fs20, \par, etc.
    clean = re.sub(r'{\\[^}]+}', '', clean)          # elimina bloques como {\fonttbl...}
    clean = re.sub(r'[{}]', '', clean)               # elimina llaves
    clean = re.sub(r'\r?\n', ' ', clean)             # elimina saltos de línea
    return clean.strip()