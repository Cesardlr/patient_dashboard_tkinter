# 📋 Instrucciones para Ejecutar el Programa

## 1. Crear el archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Server Configuration
PORT=5000
NODE_ENV=development

# PostgreSQL Configuration (Docker)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medico_db
DB_USER=admin
DB_PASSWORD=admin123

# PostgreSQL Alternative Names (for compatibility)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=medico_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123

# MongoDB Configuration (Docker)
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=medico_mongo
MONGO_USER=app_user
MONGO_PASSWORD=app_password

# JWT Configuration
JWT_SECRET=282e65ba779b391c3f65c5f846369fc1
JWT_EXPIRES_IN=24h

# CORS
CORS_ORIGIN=http://localhost:3000
```

## 2. Asegúrate de que Docker esté corriendo

Asegúrate de que tu contenedor de PostgreSQL en Docker esté corriendo y accesible en `localhost:5432`.

## 3. Instalar dependencias

### Opción A: Con entorno virtual (recomendado)

```powershell
# Crear entorno virtual (si no existe)
py -3.9 -m venv venv39

# Activar entorno virtual
.\venv39\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Opción B: Instalación global

```powershell
pip install -r requirements.txt
```

## 4. Ejecutar el programa

```powershell
python patient_dashboard.py
```

## ⚠️ Notas importantes

- El programa se conectará a PostgreSQL usando las credenciales del archivo `.env`
- Asegúrate de que el contenedor Docker de PostgreSQL esté corriendo antes de ejecutar el programa
- Si cambias las credenciales en `.env`, reinicia el programa para que tome los nuevos valores
