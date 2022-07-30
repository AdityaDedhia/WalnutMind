from . base import *

# Use admin mails instead of sentry for staging error handling.
ADMINS = [
	('Aditya Dedhia', 'aditya23dedhia@gmail.com'),
]

ALLOWED_HOSTS = ['www.halflife-edu-dev.herokuapp.com', 'halflife-edu-dev.herokuapp.com']

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.environ['DEVDBName'],
		'HOST': os.environ['DEVDBHost'],
		'PORT': 5432,
		'USER': os.environ['DEVDBUser'],
		'PASSWORD': os.environ['DEVDBPass'],
	}
}

MIDDLEWARE = MIDDLEWARE + [
	'debug_toolbar.middleware.DebugToolbarMiddleware',  # DEBUG TOOLBAR
]

INSTALLED_APPS = INSTALLED_APPS + [
	'debug_toolbar',
]

AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_TEST_BUCKET_NAME']

INTERNAL_IPS = [  # Debugging IPs
	os.environ['OWNER_IP'],
]
