from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField
from ckeditor_uploader.fields import RichTextUploadingField
from Blog.utils import image_resize


class Term(models.Model):
    term = models.CharField(max_length=128, blank = False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='termcreator')
    cover = models.ImageField(upload_to = 'Wiki/term_covers', blank = True, null = True)
    coverSrc = models.CharField(max_length = 128, blank = True, null = True)
    coverURL = models.URLField(max_length = 255, blank = True, null = True)
    slug = AutoSlugField(populate_from='term', unique = True, null = True, default = None)
    definition = models.TextField(blank = False, max_length=1000)
    dateUpdated = models.DateTimeField(auto_now = True)
    verified = models.BooleanField(default = False)

    def __str__(self):
        return str(self.term)

    def save(self, *args, **kwargs):
        if self.cover:
            image_resize(self.cover, 800, 600)
            super().save(*args, **kwargs)

class List(models.Model):
    title = models.CharField(max_length=128, blank = False, unique=True)
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="listpublisher")
    description = models.CharField(max_length = 255, null = True, blank = True)
    terms = models.ManyToManyField(Term)
    public = models.BooleanField(default = False)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.title)

class Resource(models.Model):
    title = models.CharField(max_length=100, blank = False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null = True, blank = True)
    source = models.CharField(max_length = 50, blank = False)
    isbnlink = models.CharField(null = True, blank = True, max_length=13)
    weblink = models.URLField(null = True, blank = True)
    videolink = EmbedVideoField(null = True, blank = True)
    filelink = models.FileField(upload_to = 'Wiki/Resources', null = True, blank = True)
    text = RichTextUploadingField(blank = True)
    description = models.CharField(max_length = 255, blank = True)
    dateCreated = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.title)

class Collection(models.Model):
    title = models.CharField(max_length=128, blank = False, unique=True)
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    description = models.CharField(max_length = 255, null = True, blank = True)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="collectionpublisher")
    contributors = models.ManyToManyField(User, blank = True)
    resources = models.ManyToManyField(Resource)
    public = models.BooleanField(default = True)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.title)