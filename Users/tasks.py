from __future__ import absolute_import, unicode_literals

from celery import shared_task
from django.core.mail import send_mail


@shared_task(name="send_subscriber_task")
def send_subscriber_task(subject, message, from_email, to_email):
	send_mail(subject, message, from_email, to_email)
	return True
