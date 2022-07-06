from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from taggit.managers import TaggableManager
from autoslug import AutoSlugField
from Blog.utils import image_resize

class Post(models.Model):
    title = models.CharField(max_length=128, blank = False) #Blank=false for required fields
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    cover = models.ImageField(upload_to = 'Articles/article_covers', blank = False)
    coverSrc = models.CharField(max_length = 128)
    coverURL = models.URLField(max_length = 255)
    author = models.ForeignKey(User, on_delete= models.CASCADE, related_name="articlepublisher")
    abstract = models.CharField(max_length=255, blank = False)
    tags = TaggableManager(related_name="articletags")
    content = RichTextUploadingField(blank = False)
    resources = RichTextField(blank = True)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)
    public = models.BooleanField(default = False)
    was_public = models.BooleanField(default = False)
    likes = models.ManyToManyField(User, related_name="article_likes", blank = True)
    saves = models.ManyToManyField(User, related_name="article_saves", blank = True)


    def __str__(self):
        return str(self.title)

    def total_likes(self):
        return self.likes.count()

    def total_saves(self):
        return self.saves.count()

    def get_absolute_url(self): #REDIRECT TO PAGE WHEN MODEL IS UPDATED
        return reverse('articleview', kwargs={'pk_slug': str(self.slug)})
    
    def save(self, *args, **kwargs):
        image_resize(self.cover, 1200, 900)
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name = "articlecomments", on_delete= models.CASCADE)
    content = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete= models.CASCADE, related_name="articlecommentauthor")
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ['-dateCreated']

    def __str__(self):
        return str(self.author)