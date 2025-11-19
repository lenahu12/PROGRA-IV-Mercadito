import os
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent








# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="unsafe-secret-key")



#Config para Render y Debug.
DEBUG = config("DEBUG", default=True, cast=bool)
RENDER = config("RENDER", default=False, cast=bool)
SITE_ID = 1

ALLOWED_HOSTS = ["*"]


# Application definition

BASICS= [
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
]

INSTALLED_APPS = BASICS + TERCEROS + PROPIAS
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",  # servir estáticos en Render.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware", # sin esto allauth no funciona.
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
AUTH_USER_MODEL = 'users.CustomUser'


# redirecciones de Allauth y otras configuraciones:
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage' # Para poder generar una alerta de logout.
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = False
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
#-------------------------------------

ROOT_URLCONF = 'myproject.urls'

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



WSGI_APPLICATION = 'myproject.wsgi.application'




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
STATICFILES_DIRS = [BASE_DIR / "static"] 
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

