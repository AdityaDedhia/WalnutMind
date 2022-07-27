from . base import *

# Use admin mails instead of sentry for staging error handling.
ADMINS = [
	('Aditya Dedhia', 'aditya23dedhia@gmail.com'),
]

DEBUG = False
SECURE_SSL_REDIRECT = True # Redirect all non-HTTPS requests to HTTPS

ALLOWED_HOSTS = ['127.0.0.1', 'www.halflife-edu-dev.herokuapp.com', 'halflife-edu-dev.herokuapp.com']

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ['TESTDBName'],
		'HOST': os.environ['TESTDBHost'],
		'PORT': 5432,
		'USER': os.environ['TESTDBUser'],
		'PASSWORD': os.environ['TESTDBPass'],
	}
}

MIDDLEWARE = MIDDLEWARE + [
	'debug_toolbar.middleware.DebugToolbarMiddleware',  # DEBUG TOOLBAR
]

INSTALLED_APPS = INSTALLED_APPS + [
	'debug_toolbar',
]

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_TEST_BUCKET_NAME']

