

---
# PROGRA-IV – Mercadito  

Proyecto desarrollado en **Python 3.10** y **Django**, hosteado en **PythonAnywhere**.  
Incluye integración con **Mercado Pago**, **Django Channels**, **autenticación con Google**, WebSockets y otras funcionalidades adicionales.

---

## 🚀 Tecnologías utilizadas

- **Python 3.10**
- **Django**
- **Django Channels**
- **Redis** (para WebSockets)
- **Autenticación con Google (django-allauth)**
- **Mercado Pago Checkout**
- **SQLite / MySQL**
- **PythonAnywhere** (Hosting)

---

## ⚙️ Instalación y ejecución local

Cloná el repositorio y ejecutá estos pasos **en orden**:

```bash
py -3.10 -m venv venv
source venv/Scripts/activate    # En Windows
# source venv/bin/activate      # En Linux/Mac

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

# Inicializa las SocialApps (Google Auth)
python manage.py init_socialapps

python manage.py migrate

# Ejecutar el servidor local
python manage.py runserver
```

## 🌱 Variables de entorno necesarias (.env)

Para que el proyecto funcione correctamente, es necesario crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

### 🔹 Configuración general
SITE_ID=1
---
### 🔹 Mercado Pago (entorno de prueba)
MP_PUBLIC_KEY_TEST=
MP_ACCESS_TOKEN_TEST=
MP_PUBLIC_KEY_APP=
MP_ACCESS_TOKEN_APP=
MERCADOPAGO_ACCESS_TOKEN_APP=
### 🔹 Mercado Pago (producción)
MP_PUBLIC_KEY_PROD=
MP_ACCESS_TOKEN_PROD=
---
### 🔹 Gmail (para envío de mails)
EMAIL_HOST_PASSWORD=
EMAIL_HOST_USER=
---
### 🔹 Django
SECRET_KEY=
---
### 🔹 Google OAuth (django-allauth)
GOOGLE_CLIENT_ID=
GOOGLE_SECRET=
---
### 🔹 Base de datos MySQL (PythonAnywhere)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
