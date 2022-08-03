from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blog.settings')

app = Celery('Blog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
	BROKER_URL=settings.BROKER_URL, )
app.autodiscover_tasks()  # Look for tasks files within apps
