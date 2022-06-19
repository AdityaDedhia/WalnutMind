from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, DO_NOTHING
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
from taggit.managers import TaggableManager


class Post(models.Model):
    title = models.CharField(max_length=128, blank = False) #Blank=false for required fields
    slug = AutoSlugField(populate_from='title', unique = False, null = True, default = None)
    author = models.ForeignKey(User, on_delete= models.CASCADE, related_name="diarypublisher")
    tags = TaggableManager(related_name="diarytags")
    content = RichTextUploadingField(blank = False)
    public = models.BooleanField(default = False)
    dateCreated = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.title)