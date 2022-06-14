from datetime import datetime
from email.policy import default
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django_countries.fields import CountryField
from ckeditor.fields import RichTextField
from Blog.utils import image_resize


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default = False)
    banner = models.ImageField(upload_to = 'Users/profile_banners', null = True, blank = True)
    avatar = models.ImageField(upload_to = 'Users/profile_covers', null = True, blank = True)
    location = CountryField(null = True)
    bio = RichTextField(max_length=2000, null = True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        image_resize(self.banner, 1200, 600)
        image_resize(self.avatar, 200, 200)
        super().save(*args, **kwargs)