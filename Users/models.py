from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from Blog.utils import image_resize
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default = False)
    avatar = models.ImageField(upload_to = 'Users/profile_covers', null = True, blank = True)
    banner = models.ImageField(upload_to = 'Users/profile_banners', null = True, blank = True)
    ip = models.GenericIPAddressField(null = True, blank = True, max_length = 32)
    location = CountryField(null = True)
    interests = models.CharField(max_length = 75, null = True, blank = True)
    tags = TaggableManager(related_name="profiletags")
    bio = models.TextField(max_length=300, null = True, blank = True)
    blog = models.CharField(max_length=255, null = True, blank = True)
    meta = RichTextField(null = True, blank = True)
    following = models.ManyToManyField(User, related_name="following", blank = True)
    is_public = models.BooleanField(default=False)
    is_author = models.BooleanField(default = False)


    def __unicode__(self):
        return str(self.user)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.banner:
            image_resize(self.banner, 2000, 1400)
        if self.avatar:
            image_resize(self.avatar, 200, 200)
        super().save(*args, **kwargs)

class Blacklist(models.Model):
    ip = models.GenericIPAddressField()
    reason = models.CharField(max_length=255)
    datelog = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.ip)

class Highlight(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=255, blank = False)
    sourcename = models.CharField(max_length=255, blank = False)
    sourcelink = models.URLField()
    tags = TaggableManager(related_name="highlighttags")

    def __str__(self):
        return str(self.content)

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, null = True, blank = True)
    link = models.URLField(blank = True, null = True)
    datelog = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.description)