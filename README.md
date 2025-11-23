# PatientDashboard – Tkinter + Avatar IA + PostgreSQL

Este proyecto implementa un **dashboard de paciente en Tkinter** con:

- 🔹 Avatar médico IA (WebView2 / Edge / CEF según OS)
- 🔹 Datos reales desde PostgreSQL
- 🔹 Login por usuario
- 🔹 Vista de condiciones, información general y archivos médicos
- 🔹 Vista con scroll + tablas + previsualización de imágenes/PDF

Funciona en **Windows, macOS y Linux**.

---

# 🖥 Requisitos previos

## 1. Python 3.9 (obligatorio)
El proyecto debe correr en un entorno virtual llamado `venv39`.

### Windows
```powershell
winget install Python.Python.3.9
macOS (Intel/M1/M2/M3)
bash
Copiar código
brew install python@3.9
Linux (Ubuntu/Debian/Fedora/Arch)
bash
Copiar código
sudo apt install python3.9 python3.9-venv -y
(En Arch: sudo pacman -S python39 si está disponible en AUR)

2. PostgreSQL
Debe estar en funcionamiento.
Valores por defecto:

yaml
Copiar código
host: localhost
port: 5432
database: ai_med_db
user: postgres
password: root
Puedes cambiarlos en el código.

⚙ Instalación por sistema operativo
🪟 WINDOWS
1. Crear el entorno virtual
powershell
Copiar código
py -3.9 -m venv venv39
2. Activarlo
powershell
Copiar código
.\venv39\Scripts\activate
3. Instalar dependencias
powershell
Copiar código
pip install -r requirements.txt
4. Ejecutar
powershell
Copiar código
python PatientDashboard.py
🍎 MACOS (INTEL y APPLE SILICON M1/M2/M3)
⚠ Nota importante
macOS no tiene WebView2.
PyWebview usará Safari WKWebView, que funciona perfecto.

1. Crear el entorno
bash
Copiar código
python3.9 -m venv venv39
2. Activar
bash
Copiar código
source venv39/bin/activate
3. Instalar requirements
bash
Copiar código
pip install -r requirements.txt
macOS puede requerir esto adicionalmente:

bash
Copiar código
pip install pyobjc
4. Ejecutar
bash
Copiar código
python PatientDashboard.py
🐧 LINUX (Ubuntu/Debian/Fedora/Arch)
1. Instalar dependencias del sistema
bash
Copiar código
sudo apt install python3.9 python3.9-venv python3.9-dev -y
sudo apt install libgtk-3-dev libwebkit2gtk-4.0-dev -y
(Las últimas dos son para WebKitGTK, navegador de pywebview.)

2. Crear el entorno
bash
Copiar código
python3.9 -m venv venv39
3. Activarlo
bash
Copiar código
source venv39/bin/activate
4. Instalar requirements
bash
Copiar código
pip install -r requirements.txt
5. Ejecutar
bash
Copiar código
python PatientDashboard.py
📁 requirements.txt
txt
Copiar código
tk
psycopg2-binary
requests
pillow
pywebview
Linux/macOS adicionales si hay errores:
txt
Copiar código
pyobjc
🔑 Configurar credenciales
En PatientDashboard.py cambia:

python
Copiar código
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ai_med_db",
    "user": "postgres",
    "password": "root"
}
🔐 Credenciales de prueba
Usuario	Password	Perfil
paciente1	root	Paciente
paciente2	root	Paciente
doctor1	root	Médico
admin1	root	Admin/Demo

▶️ Cómo correr el programa
1. Activar entorno
Windows:

powershell
Copiar código
.\venv39\Scripts\activate
macOS/Linux:

bash
Copiar código
source venv39/bin/activate
2. Ejecutar
bash
Copiar código
python PatientDashboard.py
❗ Problemas comunes
❗ psycopg2 error
php
Copiar código
pip install psycopg2-binary
❗ WebView blanco
En Windows requiere Edge WebView2:

nginx
Copiar código
winget install Microsoft.EdgeWebView2Runtime
❗ PDF no abre
Se abre en navegador externo (es normal).

❗ Imágenes no cargan
Reinstalar Pillow:

css
Copiar código
pip install pillow --force-reinstall