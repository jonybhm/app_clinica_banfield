import os
import winreg
import webbrowser
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
import subprocess
import os


def mostrar_dialogo_libreoffice(parent=None):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("LibreOffice no detectado")
    msg.setText(
        "No se encontró LibreOffice instalado.\n\n"
        "Las funciones de informes estarán deshabilitadas."
    )
    msg.setInformativeText("¿Desea instalar LibreOffice ahora?")

    btn_instalar = msg.addButton("Instalar LibreOffice", QMessageBox.AcceptRole)
    btn_continuar = msg.addButton("Continuar sin informes", QMessageBox.RejectRole)

    msg.setDefaultButton(btn_instalar)

    msg.exec_()

    if msg.clickedButton() == btn_instalar:
        return "install"
    else:
        return "skip"


def libreoffice_instalado():
    posibles_rutas = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return True

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\LibreOffice\UNO\InstallPath"
        )
        path, _ = winreg.QueryValueEx(key, "")
        if os.path.exists(os.path.join(path, "soffice.exe")):
            return True
    except:
        pass

    return False
