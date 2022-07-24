from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField
from ckeditor_uploader.fields import RichTextUploadingField
from Blog.utils import image_resize
from .validators import validate_file_size
from django.db.models.functions import Lower
from django.urls import reverse

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

    class Meta:
        ordering = [Lower('term')] #Case insensitive

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

class Collection(models.Model):
    title = models.CharField(max_length=128, blank = False, unique=True)
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    cover = models.ImageField(upload_to = 'Wiki/collection_covers', blank = True, null = True)
    description = models.CharField(max_length = 255, null = True, blank = True)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="collectionpublisher")
    contributors = models.ManyToManyField(User, blank = True)
    public = models.BooleanField(default = False)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.title)

    class Meta:
        ordering = [Lower('title')] #Case insensitive
    
    def save(self, *args, **kwargs):
        if self.cover:
            image_resize(self.cover, 1000, 700)
        super().save(*args, **kwargs)

class Resource(models.Model):
    title = models.CharField(max_length=100, blank = True, unique=False)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, null = True, blank = True)
    description = models.CharField(max_length = 255, blank = True, null = True)
    source = models.CharField(max_length = 50, blank = True, null = True)
    collection = models.ManyToManyField(Collection, related_name="resources", through='CollectionOrder')

    text = RichTextUploadingField(blank = True, null = True)

    filelink = models.FileField(upload_to = 'Wiki/Resources', null = True, blank = True)
    filetype = models.CharField(max_length = 10, blank = True, null = True)

    weblink = models.URLField(null = True, blank = True)
    webicon = models.URLField(null = True, blank = True)
    webdescription = models.CharField(max_length = 255, blank = True, null = True)

    videolink = EmbedVideoField(null = True, blank = True)
    videochannel = models.CharField(max_length = 255, blank = True, null = True)
    videodescription = models.CharField(max_length = 255, blank = True, null = True)

    isbnlink = models.CharField(null = True, blank = True, max_length=13)

    public = models.BooleanField(default = False)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)

    FILE = 'FILE'
    DOC = 'DOC'
    IMG = 'IMG'
    WEB = 'WEB'
    VIDEO = 'VIDEO'
    BOOK = 'BOOK'
    
    CHOICES = [
        (FILE, 'File'),
        (DOC, 'WM Document'),
        (IMG, 'Image'),
        (WEB, 'Web Page'),
        (VIDEO, 'YT Video'),
        (BOOK, 'Book'),
    ]
    category = models.CharField(
        max_length=5,
        choices=CHOICES,
        default=FILE,
    )
    
    def __str__(self):
        return str(self.category) + str(self.title)

    class Meta:
        ordering = ['-dateCreated']


    def clean(self):
        if self.filelink:
            validate_file_size(self.filelink)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self): #REDIRECT TO PAGE WHEN MODEL IS UPDATED
        return None


class CollectionOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    dateCreated = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return str(self.resource.title)

    class Meta:
        ordering = ['order']