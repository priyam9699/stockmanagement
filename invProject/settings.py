from pathlib import Path, os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Keep the secret key safe
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')

# Debug setting
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'invApp',
    'crispy_forms',
    'crispy_bootstrap5',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL and WSGI
ROOT_URLCONF = 'invProject.urls'
WSGI_APPLICATION = 'invProject.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Database configuration
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///{}'.format(os.path.join(BASE_DIR, 'db.sqlite3')),
        conn_max_age=600,
        ssl_require=True
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'invApp', 'assets')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Login/Logout redirects
LOGIN_REDIRECT_URL = 'product_list'
LOGOUT_REDIRECT_URL = 'product_list'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap5'
