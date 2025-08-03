# settings.py - Complete Configuration

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-development-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']

# Allowed hosts configuration - SINGLE DEFINITION
ALLOWED_HOSTS = []

if os.getenv('VERCEL'):
    # Vercel environment - allow all Vercel domains
    ALLOWED_HOSTS = ['*.vercel.app', '.vercel.app']
elif DEBUG:
    # Development environment
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    # Production environment - add your specific domains
    ALLOWED_HOSTS = [
        'your-domain.com',  # Replace with your actual domain
        '*.vercel.app',
        '.vercel.app'
    ]

# Add custom hosts from environment variable
custom_hosts = os.getenv('ALLOWED_HOSTS', '')
if custom_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in custom_hosts.split(',') if host.strip()])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'auth_google'
]

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

ROOT_URLCONF = 'return_mgm.urls'

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

WSGI_APPLICATION = 'return_mgm.wsgi.application'

# Database Configuration - Smart switching
def get_database_config():
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Production database (Render/Supabase/etc.)
        import dj_database_url
        config = dj_database_url.parse(database_url)
        
        # Add SSL requirement for production
        config['OPTIONS'] = config.get('OPTIONS', {})
        config['OPTIONS']['sslmode'] = 'require'
        config['CONN_MAX_AGE'] = 600
        config['CONN_HEALTH_CHECKS'] = True
        
        return {'default': config}
    else:
        # Local development database (SQLite)
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

DATABASES = get_database_config()

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
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Static files directories
STATICFILES_DIRS = []

# Only add static dir if it exists (to avoid warnings)
static_dir = BASE_DIR / 'static'
if static_dir.exists():
    STATICFILES_DIRS.append(static_dir)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Google OAuth settings (if using)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

print(f"DEBUG: {DEBUG}")
print(f"DATABASE: {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")