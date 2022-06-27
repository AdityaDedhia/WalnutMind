from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from embed_video.fields import EmbedVideoField

class Term(models.Model):
    term = models.CharField(max_length=128, blank = False, unique=True)
    slug = AutoSlugField(populate_from='term', unique = True, null = True, default = None)
    definition = models.TextField(blank = False, max_length=300)
    dateUpdated = models.DateTimeField(auto_now = True)
    verified = models.BooleanField(default = False)

    def __str__(self):
        return str(self.term)

class List(models.Model):
    title = models.CharField(max_length=128, blank = False)
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="listpublisher")
    description = models.CharField(max_length = 255, null = True, blank = True)
    terms = models.ManyToManyField(Term)
    public = models.BooleanField(default = True)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.title)

class Resource(models.Model):
    title = models.CharField(max_length=100, blank = False)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null = True, blank = True)
    source = models.CharField(max_length = 50, blank = False)
    isbnlink = models.CharField(null = True, blank = True, max_length=13)
    weblink = models.URLField(null = True, blank = True)
    videolink = EmbedVideoField(null = True, blank = True)
    filelink = models.FileField(upload_to = 'Wiki/Resources', null = True, blank = True)
    description = models.CharField(max_length = 255, blank = True)
    dateCreated = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.title)

class Collection(models.Model):
    title = models.CharField(max_length=128, blank = False)
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