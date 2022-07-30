from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from Blog.utils import image_resize
from django.urls import reverse
from hitcount.models import HitCount
from django.contrib.contenttypes.fields import GenericRelation


class Post(models.Model):
    title = models.CharField(max_length=128, blank=False)
    slug = AutoSlugField(populate_from='title', unique=False, null=True, default=None)
    cover = models.ImageField(upload_to='Blogs/blog_covers', blank=False)
    coverSrc = models.CharField(max_length=128)
    coverURL = models.URLField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="diarypublisher")
    tags = TaggableManager(related_name="diarytags")
    content = RichTextUploadingField(blank=False)
    dateCreated = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    views = GenericRelation(HitCount, object_id_field='object_pk', related_name="diary_views"),
    likes = models.ManyToManyField(User, related_name="diary_likes", blank=True)
    saves = models.ManyToManyField(User, related_name="diary_saves", blank=True)

    def __str__(self):
        return str(self.title)

    def total_likes(self):
        return self.likes.count()

    def total_saves(self):
        return self.saves.count()

    def get_absolute_url(self):  # REDIRECT TO PAGE WHEN MODEL IS UPDATED
        return reverse('blogview', kwargs={'username': str(self.author), 'pk_slug': str(self.slug)})

    def save(self, *args, **kwargs):
        image_resize(self.cover, 1200, 900)
        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="diarycomments", on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete= models.CASCADE, related_name="diarycommentauthor")
    dateCreated = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-dateCreated']

    def __str__(self):
        return str(self.author)
