# Patient Dashboard - Tkinter

Dashboard de paciente con interfaz Tkinter que incluye:

- 🔹 Avatar médico IA (se abre automáticamente después del login)
- 🔹 Información del paciente desde PostgreSQL
- 🔹 Visualización de archivos médicos

---

## 📋 Requisitos

- Python 3.9+
- PostgreSQL en ejecución
- Archivo `.env` con las credenciales de la base de datos

---

## 🚀 Pasos para ejecutar

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos

Crea un archivo `.env` en la raíz del proyecto con:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medico_db
DB_USER=admin
DB_PASSWORD=admin123
```

O modifica directamente `DB_CONFIG` en `patient_dashboard.py` si prefieres.

### 3. Ejecutar la aplicación

```bash
python patient_dashboard.py
```

---

## 🔑 Login

Después de ejecutar, ingresa tus credenciales en la pantalla de login. El avatar se abrirá automáticamente después de un login exitoso.

---

## ⚠️ Notas

- **Windows**: Requiere Edge WebView2 Runtime para el avatar
- **macOS/Linux**: Usa WebKit nativo del sistema
- El avatar se abre en una ventana separada con EdgeChromium

---

## 📦 Dependencias principales

- `tkinter` - Interfaz gráfica
- `psycopg2-binary` - Conexión a PostgreSQL
- `pywebview` - Ventana del avatar
- `pillow` - Manejo de imágenes
- `python-dotenv` - Variables de entorno
- `bcrypt` - Hashing de contraseñas
