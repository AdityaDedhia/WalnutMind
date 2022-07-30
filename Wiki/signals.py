from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from . models import Resource
from Articles.models import Post as articlePost
from Commentaries.models import Post as commentaryPost
from Diaries.models import Post as diaryPost

from django.core.cache import cache
from .views import RESOURCES_KEY


@receiver(post_save, sender=articlePost)
def create_article_resource(sender, instance, created, **kwargs):
	if created:  # Occurs upon save of article post
		Resource.objects.create(
			title=instance.title,
			creator=instance.author,
			description=instance.abstract,
			source=str(instance.author.first_name + " " + instance.author.last_name),
			pubpk=instance.pk,
			category='ARTICLE'
		)
		cache.delete(RESOURCES_KEY)  # Delete old resource cache


@receiver(pre_delete, sender=articlePost)
def delete_article_resource(sender, instance, **kwargs):
	article = Resource.objects.get(category='ARTICLE', creator=instance.author, pubpk=instance.pk)
	article.delete()
	cache.delete(RESOURCES_KEY)  # Delete old resource cache


@receiver(post_save, sender=commentaryPost)
def create_commentary_resource(sender, instance, created, **kwargs):
	if created:  # Occurs upon save of article post
		Resource.objects.create(
			title=instance.title,
			creator=instance.publisher,
			description=instance.abstract,
			source=str(instance.publisher.first_name + " " + instance.publisher.last_name),
			pubpk=instance.pk,
			category='COMMENTARY'
		)
		cache.delete(RESOURCES_KEY)  # Delete old resource cache


@receiver(pre_delete, sender=commentaryPost)
def delete_commentary_resource(sender, instance, **kwargs):
	commentary = Resource.objects.get(category='COMMENTARY',
	                                  creator=instance.publisher, pubpk=instance.pk)
	commentary.delete()
	cache.delete(RESOURCES_KEY)  # Delete old resource cache


@receiver(post_save, sender=diaryPost)
def create_diary_resource(sender, instance, created, **kwargs):
	if created:  # Occurs upon save of article post
		Resource.objects.create(
			title=instance.title,
			creator=instance.author,
			description=instance.abstract,
			source=str(instance.author.first_name + " " + instance.author.last_name),
			pubpk=instance.pk,
			category='BLOG'
		)
		cache.delete(RESOURCES_KEY)  # Delete old resource cache


@receiver(pre_delete, sender=diaryPost)
def delete_diary_resource(sender, instance, **kwargs):
	diary = Resource.objects.get(category='BLOG', creator=instance.author, pubpk=instance.pk)
	diary.delete()
	cache.delete(RESOURCES_KEY)  # Delete old resource cache
