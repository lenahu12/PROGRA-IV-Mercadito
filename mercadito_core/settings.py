import os
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages
from pathlib import Path
from dotenv import load_dotenv
import socket
# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="unsafe-secret-key")

#Config para Render y Debug.
DEBUG = config("DEBUG", default=True, cast=bool)
RENDER = config("RENDER", default=False, cast=bool)

hostname = socket.gethostname()

if "localhost" in hostname or "127.0.0.1" in hostname:
    SITE_ID = 1  # local
else:
    SITE_ID = 2  # ngrok o producción

ALLOWED_HOSTS = ["*"]
#para que permita ngrok
CSRF_TRUSTED_ORIGINS = [
    "https://brantlee-greasy-rosella.ngrok-free.dev",
]

# Aspectos de manejo de sesión:
SESSION_COOKIE_AGE = 30 * 60  #tiempo de sesion
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

#Configuración de mercado pago:
load_dotenv()
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN_TEST")  # cambiar a PROD en producción
MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY_TEST")
MERCADOPAGO_ACCESS_TOKEN = config("MERCADOPAGO_ACCESS_TOKEN")




# Application definition
BASICS= [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]
TERCEROS = [
    'rest_framework',
    'allauth',
    'allauth.account',
    "allauth.socialaccount",  
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
]
PROPIAS = [
    'users',
    'products',
    'scraping',
    'presence',
    'chat',
    'quotes',
    'orders',
]

INSTALLED_APPS = BASICS + TERCEROS + PROPIAS
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # servir estáticos en Render.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'presence.middleware.UpdateLastSeenMiddleware', #import del lastSeen hecho en la app presence
    'presence.middleware.AutoLogoutMiddleware', #import del autoLogout en la app presence
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # sin esto allauth no funciona.
]


#---------- para allauth ------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_USER_MODEL = "users.CustomUser"


# redirecciones de Allauth y otras configuraciones:
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage' # Para poder generar una alerta de logout.
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True
#------------------------------------- Configuración de mails
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

ROOT_URLCONF = 'mercadito_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"], #carpeta de templates.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#Para el funcionamiento de channels.
ASGI_APPLICATION = "mercadito_core.asgi.application"
WSGI_APPLICATION = 'mercadito_core.wsgi.application'




#------------------------ condicional para que funcione tanto en Render como local: base de datos -----------------------
if RENDER:
    DATABASES = {
        "default": dj_database_url.config(
            default=config("DATABASE_URL")
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
#--------------------------------------------------------------------------------------------------------------------


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
#-------------------------------- imagenes -----------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "media",  # agregado temporalmente para servir imágenes
]

MEDIA_ROOT = BASE_DIR / "media"  #para imagenes dentro del proyecto
MEDIA_URL = "/media/"      #para imagenes de internet
#-------------------------------- imagenes -----------------------------------------------

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

#----------Codigo salvador que hizo funcionar el WebSocket para el chat. TE QUIERO CHANNEL_LAYERS ------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

