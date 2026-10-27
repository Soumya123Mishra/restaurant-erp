from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-your-secret-key-here-change-me'
ROOT_URLCONF = 'restaurant_erp.urls'

# 1. MIDDLEWARE में यह लाइन्स होनी चाहिए:
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

# 2. TEMPLATES की यह सेटिंग होनी चाहिए:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

INSTALLED_APPS = [
    'django_mongodb_backend',
    'restaurant_erp.apps.MongoAdminConfig',
    'restaurant_erp.apps.MongoAuthConfig',
    'restaurant_erp.apps.MongoContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'restaurant_erp.apps.CoreConfig',
]

import django_mongodb_backend

DATABASES = {
    'default': django_mongodb_backend.parse_uri(
        'mongodb+srv://mishrasoumya951_db_user:soumyamishra@cluster0.jbc02ot.mongodb.net/restaurant_db?retryWrites=true&w=majority'
    )
}
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
DEBUG = True
ALLOWED_HOSTS =  ['*']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'llzfwbw6',
    'API_KEY': '113785445944453',
    'API_SECRET': 'QEJXPGtVxn2l7DT4UU-xHZlbL-0',
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard-redirect/'