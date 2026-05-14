"""
Настройки Django-проекта bookclub.

Для учебных целей: настройки разбиты на блоки с комментариями,
чтобы было понятно, за что отвечает каждый раздел.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────
# БЕЗОПАСНОСТЬ
# ──────────────────────────────────────────────
SECRET_KEY = 'django-insecure-bookclub-dev-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ──────────────────────────────────────────────
# ПРИЛОЖЕНИЯ
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Наше приложение
    'clubs',

    # Инструмент профилирования — показывает SQL-запросы прямо на странице
    'debug_toolbar',
]

# ──────────────────────────────────────────────
# MIDDLEWARE
# ──────────────────────────────────────────────
MIDDLEWARE = [
    # debug_toolbar должен идти как можно раньше
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookclub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookclub.wsgi.application'

# ──────────────────────────────────────────────
# БАЗА ДАННЫХ — PostgreSQL
# ──────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bookclub',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ──────────────────────────────────────────────
# ЛОКАЛИЗАЦИЯ
# ──────────────────────────────────────────────
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Tomsk'
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# СТАТИЧЕСКИЕ ФАЙЛЫ
# ──────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────
# DJANGO DEBUG TOOLBAR
# ──────────────────────────────────────────────
# Toolbar показывается только для этих IP-адресов
INTERNAL_IPS = [
    '127.0.0.1',
]
