import pyodbc

server = 'SERVER'
database = 'ICB'
username = 'sa'
password = 'Comeba.1'

try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.databases")
    print("Bases de datos en el servidor:")
    for row in cursor.fetchall():
        print("-", row.name)
    conn.close()
except Exception as e:
    print("Error de conexión:", e)
