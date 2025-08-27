
import pyodbc
#from acceso_db.config import RUTA_ACCESS

RUTA_ACCESS = r"C:\Users\Jonathan\Desktop\python\JONATHAN\EXPORTADA_ACCESS.mdb"

def buscar_valor_en_bd(valor_busqueda):
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={RUTA_ACCESS};"
    )
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    tablas = []
    for row in cursor.tables(tableType='TABLE'):
        tablas.append(row.table_name)

    print(f"🔍 Buscando '{valor_busqueda}' en {len(tablas)} tablas...\n")

    for tabla in tablas:
        try:
            cursor.execute(f"SELECT * FROM [{tabla}]")
            columnas = [column[0] for column in cursor.description]
            for columna in columnas:
                query = f"SELECT TOP 1 * FROM [{tabla}] WHERE [{columna}] LIKE ?"
                try:
                    cursor.execute(query, f"%{valor_busqueda}%")
                    if cursor.fetchone():
                        print(f"✔ Encontrado en: {tabla} → columna: {columna}")
                except:
                    continue  # Por si hay problemas de tipo de datos
        except:
            continue  # Por si la tabla no se puede consultar

    cursor.close()
    conn.close()
    

# USO:
buscar_valor_en_bd("3767081")
