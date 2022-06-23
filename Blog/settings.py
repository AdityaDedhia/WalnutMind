import os
import dotenv
from pathlib import Path

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

#PRODUCTION SETTINGS ---------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'www.walnutmind.org', 'walnutmind.org']

# CONFIG SETTINGS ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

#ENV VARIABLES
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
SECRET_KEY = os.environ['SECRET_KEY']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'axes',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.postgres',
    'django_countries',
    'ckeditor',
    'ckeditor_uploader',
    'bootstrap_modal_forms',
    'storages',
    'taggit',
    'rest_framework',
    'reset_migrations',
    'Users',
    'Articles',
    'Commentaries',
    'Diaries',
    'Wiki',
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
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'Blog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Blog.wsgi.application'
#https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DBName'],
        'HOST': os.environ['DBHost'],
        'PORT': 5432,
        'USER': os.environ['DBUser'],
        'PASSWORD': os.environ['DBPass'],
    }
}

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
AUTHENTICATION_BACKENDS = [
'axes.backends.AxesBackend',
'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

TAGGIT_CASE_INSENSITIVE = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#RICH TEXT EDITOR-------------
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        'height': 300,
        'width': 600,
            'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'find',
        ]),
    },

}

#FILES------------------------------------------------------------

GEOIP_PATH = os.path.join(BASE_DIR, 'geoIP')

STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = ()

MEDIA_URL = '/user_content/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'user_content')

CKEDITOR_UPLOAD_PATH = "uploads/ckeditor/"

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

AWS_S3_FILE_OVERWRITE = False #rename files uploaded with same name
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_SIGNATURE_VERSION = 's3v4'

#SETTINGS NOT WORKING IN PRODUCTION
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
#django_heroku.settings(locals())


#EMAIL FOR USER MANAGEMENT
EMAIL_FROM_USER = 'support@walnutmind.org'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'support@walnutmind.org'
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
DEFAULT_FROM_EMAIL = 'support@walnutmind.org'