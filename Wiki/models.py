from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class Term(models.Model):
    term = models.CharField(max_length=128, blank = False)
    slug = AutoSlugField(populate_from='term', unique = True, null = True, default = None)
    definition = RichTextUploadingField(blank = False)
    dateUpdated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.term)

class List(models.Model):
    title = models.CharField(max_length=128, blank = False)
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="listpublisher")
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)
    terms = models.ManyToManyField(Term)
    tags = TaggableManager(related_name="listtags")



class Resource(models.Model):
    title = models.CharField(max_length=128, blank = False)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    link = models.URLField(blank = False)
    description = models.CharField(max_length = 255, blank = True)
    dateCreated = models.DateTimeField(auto_now_add = True)


class Collection(models.Model):
    title = models.CharField(max_length=128, blank = False)
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="collectionpublisher")
    contributors = models.ManyToManyField(User)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)
    resources = models.ManyToManyField(Resource)
    tags = TaggableManager(related_name="collectiontags")
