# ICB Historias Clínicas

<div align="center">
  <img src="assets/logo/logo.png" alt="Logo" width="300" height="300">
</div>

<div align="center">
  SISTEMA DE GESTIÓN DE HISTORIAS CLÍNICAS
</div>

---

## Tabla de Contenidos

- [Sobre](#sobre)
- [Características](#características)
- [Capturas de Pantalla / Screenshots](#capturas-de-pantalla)
- [Empezando](#empezando)
  - [Hecho con](#hecho-con)
  - [Instalación](#instalación)
  - [Ejecutable](#ejecutable)
- [Autor](#autor)
- [Licencia](#licencia)
- [Reconocimientos](#reconocimientos)

---

## Sobre
**ICB Historias Clínicas** es un sistema de gestión diseñado para el ["Instituto Cardiológico Banfield"](http://www.institutocardiologicobanfield.com/quienes_somos.html). Permite organizar turnos, agendas, pacientes e informes médicos de manera centralizada, facilitando el acceso rápido y seguro a la información clínica.

---

## Características

- **Turnos y Agendas**: búsqueda de turnos por fecha y gestión de evoluciones médicas.
- **Informes**: consulta e impresión de informes de pacientes.
- **Historias Clínicas**: búsqueda e impresión del historial clínico del paciente.
- **Gestión de Pacientes**: búsqueda por nombre o DNI.
- **Instalador propio**: incluye todas las dependencias necesarias.

---

## Capturas de Pantalla

<div align="center">
<table>
<tr>
  <td><b>Menu Principal</b><br><img src="assets/screenshots/menu_ppal.png" width="300"></td>
  <td><b>Turnos</b><br><img src="assets/screenshots/turnos.png" width="300"></td>
</tr>
<tr>
  <td><b>Pacientes</b><br><img src="assets/screenshots/pacientes.png" width="300"></td>
  <td><b>Historial</b><br><img src="assets/screenshots/historial.png" width="300"></td>
</tr>
<tr>
  <td><b>Evolución</b><br><img src="assets/screenshots/evolucion.png" width="300"></td>
  <td><b>Permisos</b><br><img src="assets/screenshots/permisos.png" width="300"></td>
</tr>
</table>
</div>

---

## Empezando

### Hecho con
- **Python 3.11**
- **PyInstaller** para generar el ejecutable
- **PyQt** para la interfaz gráfica
- **MS ODBC Driver** para conexión con base de datos SQL Server

---

### Instalación
1. Clonar el repositorio:
   ```sh
   git clone https://github.com/jonybhm/app_clinica_banfield.git
   ```
2. Instalar dependencias de Python:
   ```sh
   pip install -r requirements.txt
   ```
3. Ejecutar la aplicación en modo desarrollo:
   ```sh
   python main.py
   ```

---

### Releases y Ejecutable
Para ver las versiones disponibles
[Releases](https://github.com/jonybhm/app_clinica_banfield/releases/)

Si no deseás instalar dependencias manualmente, podés descargar el **instalador oficial** aquí:  
[Descargar Instalador ICB](https://github.com/jonybhm/app_clinica_banfield/releases/download/v1.0.0/ICBHistoriaClinicaSetup-v1.0.0.exe)

El instalador ya incluye **Microsoft ODBC Driver 18 for SQL Server (x64)**, pero en caso de necesitar instalarlo manualmente descargar de aquí:  
[Descargar Instalador ODBC](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver17)

Lo mismo sucede con el **Visual C++ 2015-2019 Redistributable** necesario para ejecutar el ODBC, en caso de necesitarlo usar el siguiente link:
[Descargar Instalador Visual C++ 2015-2019](https://aka.ms/vs/17/release/vc_redist.x64.exe)
---

## Autor
Desarrollado por [Jonathan De Castro](https://github.com/jonybhm).  

---

## Licencia
Este proyecto está autorizado bajo la **Licencia MIT**.  
Consulta [LICENSE](LICENSE) para más información.

---

## Reconocimientos
- ["Instituto Cardiológico Banfield"](http://www.institutocardiologicobanfield.com/quienes_somos.html) por el caso de uso real  
- Comunidad de Python y PyInstaller  
- Inno Setup por el empaquetado del instalador