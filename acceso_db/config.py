# -*- coding: utf-8 -*-
"""
Created on Wed May 21 19:14:54 2025

@author: Jonathan
"""
import json
import os
import sys

def obtener_ruta_base():
    if getattr(sys, 'frozen', False):  
        # PyInstaller
        return sys._MEIPASS
    else:
        # código fuente
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = obtener_ruta_base()

# main.py
CONFIG_PATH = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]), "db_config.json")

# acceso_db
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = os.path.join(BASE_DIR, "db_config.json")

DEFAULT_CONFIG = {
    "server": "SERVER",
    "database": "ICB",
    "username": "sa",
    "password": "",
    "mode": "sqlserver"
}

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        user_config = json.load(f)
except FileNotFoundError:
    print(f"⚠️ No se encontró el archivo de configuración en: {CONFIG_PATH}")
    user_config = DEFAULT_CONFIG

SQLSERVER_CONFIG = {
    "server": user_config.get("server", DEFAULT_CONFIG["server"]),
    "database": user_config.get("database", DEFAULT_CONFIG["database"]),
    "username": user_config.get("username", DEFAULT_CONFIG["username"]),
    "password": user_config.get("password", DEFAULT_CONFIG["password"]),
}

MODO_CONEXION = user_config.get("mode", DEFAULT_CONFIG["mode"])
RUTA_ACCESS = user_config.get("access_path", "")