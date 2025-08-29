import os, sys

def recurso_path(rel_path):
    """Devuelve la ruta absoluta a un recurso, compatible con PyInstaller"""
    try:
        base_path = sys._MEIPASS  # Carpeta temporal cuando está empaquetado
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)
