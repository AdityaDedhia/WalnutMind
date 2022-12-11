from django.test import TestCase
from django.contrib.auth.models import User
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from Articles.models import Post


class TestArticlesPost(TestCase):
	def setUp(self):
		testerDB = User.objects.create_user(username='testerDB', password='10retset')

		self.test_root = os.path.abspath(os.path.dirname(__file__))
		self._old_MEDIA_ROOT = settings.MEDIA_ROOT
		# override MEDIA_ROOT for this test
		settings.MEDIA_ROOT = os.path.join(self.test_root, 'media')

		image = SimpleUploadedFile(
			name='test_image.jpg',
			content=open(os.path.join(self.test_root, "media/walnuts.jpg"), 'rb').read(),
			content_type='image/jpg'
		)

		self.post = Post(
			title="Walnuts are nuts",
			abstract="Walnuts have so many things to offer, continue reading to find out more.",
			tags="Nature",
			cover=image,
			coverSrc="Unsplash",
			coverURL="www.unsplash.com",
			author=testerDB,
			content="A long text about Walnuts.",
			resources="A list of resources about Walnuts."
		)
		self.post.save()

	def test_title(self):
		self.assertEquals(self.post.title, 'Walnuts are nuts')
		self.assertEquals(self.post.slug, 'walnuts-are-nuts')
