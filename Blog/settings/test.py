from . dev import *

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1']

APPEND_SLASH = False
PREPEND_WWW = False
BROKER_URL = 'amqp://guest:guest@localhost:5672/'  # Not required for tests
DEBUG = True
SECURE_SSL_REDIRECT = False  # Redirect all non-HTTPS requests to HTTPS
