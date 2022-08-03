from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, Subscriber, Mail


@receiver(post_save, sender=Profile)
def verify_existing_subscriber(sender, instance, created, **kwargs):
	if created:
		user = instance.user  # Get user 1-1 key from profile
		if Subscriber.objects.filter(email=user.email).exists():
			subscriber = Subscriber.objects.get(email=user.email)
			subscriber.user = user
			subscriber.save()


@receiver(post_save, sender=Mail)
def send_subscriber_mail(sender, instance, created, **kwargs):
	if created:

		for subscriber in Subscriber.objects.all():
			send_subscriber_task.delay(
				instance.subject, instance.message, 'support@walnutmind.org', [subscriber.email],
				fail_silently=False, )  # Celery task
