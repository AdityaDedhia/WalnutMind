from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, DO_NOTHING
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField


class Post(models.Model):
    title = models.CharField(max_length=128, blank = False) #Blank=false for required fields
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)

    content = RichTextUploadingField(blank = False)
    dateCreated = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.title)