"""
Django settings for campus_safety project.
"""
import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env 文件（优先加载项目根目录的 .env，再加载 backend 目录的 .env）
load_dotenv(BASE_DIR / '.env', override=False)
load_dotenv(BASE_DIR.parent / 'deploy' / 'windows' / '.env.production', override=False)

# Security settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-campus-safety-key-2024-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,10.252.68.246,192.168.137.1').split(',') if h.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # JWT token blacklist
    'corsheaders',
    'django_filters',
    # Local apps
    'safety',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campus_safety.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'campus_safety.wsgi.application'

# Database - 通过环境变量切换，默认 SQLite
_db_engine = os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3')
_db_name = os.environ.get('DB_NAME', '')
DATABASES = {
    'default': {
        'ENGINE': _db_engine,
        'NAME': _db_name or (BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (上传的图片)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS - 通过环境变量配置，默认开发环境白名单
_cors_origins_str = os.environ.get('CORS_ORIGINS', '')
if _cors_origins_str:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins_str.split(',') if o.strip()]
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
    ]
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '10/minute',
    },
}

# Simple JWT - 通过环境变量配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_DAYS', '1'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# File upload
_max_upload_mb = int(os.environ.get('MAX_UPLOAD_SIZE_MB', '10'))
FILE_UPLOAD_MAX_MEMORY_SIZE = _max_upload_mb * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = _max_upload_mb * 1024 * 1024

# nginx 反向代理时，Django 拿到的 request 都是 http 的。
# 加这个 header 让 Django 知道原始请求是 https，不然 DRF 生成的 URL 都是 http://
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Custom User Model
AUTH_USER_MODEL = 'safety.User'

# WeChat Mini Program Settings
WX_APPID = os.environ.get('WX_APPID', '')
WX_SECRET = os.environ.get('WX_SECRET', '')
WX_TEMPLATE_IDS = {
    'hazard_new': os.environ.get('WX_TEMPLATE_HAZARD_NEW', ''),
    'hazard_assigned': os.environ.get('WX_TEMPLATE_HAZARD_ASSIGNED', ''),
    'rectify_result': os.environ.get('WX_TEMPLATE_RECTIFY_RESULT', ''),
    'inspection_overdue': os.environ.get('WX_TEMPLATE_INSPECTION_OVERDUE', ''),
    'ai_abnormal': os.environ.get('WX_TEMPLATE_AI_ABNORMAL', ''),
}

# Django cache for WeChat access_token
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
