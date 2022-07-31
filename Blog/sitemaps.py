from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from Articles.models import Post as ArticlePost
from Commentaries.models import Post as CommentaryPost
from Diaries.models import Post as DiaryPost


class StaticSitemap(Sitemap):
	changefreq = "daily"
	priority = 1

	def items(self):
		return ['index', 'about', 'opportunities', 'contact', 'roadmap',
		        'privacy', 'terms', 'faq']

	def location(self, item):
		return reverse(item)


class ArticleSitemap(Sitemap):
	changefreq = "daily"
	priority = 0.8

	def items(self):
		return ArticlePost.objects.filter(public=True).order_by('-dateCreated')

	@staticmethod
	def lastmod(obj):
		return obj.dateUpdated


class CommentarySitemap(Sitemap):
	changefreq = "daily"
	priority = 0.6

	def items(self):
		return CommentaryPost.objects.filter(public=True).order_by('-dateCreated')

	@staticmethod
	def lastmod(obj):
		return obj.dateUpdated


class DiarySitemap(Sitemap):
	changefreq = "daily"
	priority = 0.4

	def items(self):
		return DiaryPost.objects.filter(public=True).order_by('-dateCreated')

	@staticmethod
	def lastmod(obj):
		return obj.dateUpdated
