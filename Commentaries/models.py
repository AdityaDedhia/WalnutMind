from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, DO_NOTHING
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
from Blog.utils import image_resize
from taggit.managers import TaggableManager


class Post(models.Model):
    title = models.CharField(max_length=128, blank = False) #Blank=false for required fields
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    tags = TaggableManager(related_name="commentarytags")
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentarypublisher")
    author = models.CharField(max_length = 50, blank = False)
    year = models.IntegerField(blank=False)
    authorlink = models.URLField(max_length = 128, blank = True)
    pages = models.IntegerField()
    readingEST = models.IntegerField()
    cover = models.ImageField(upload_to = 'Commentaries/commentary_covers', blank = False)
    topics = models.CharField(max_length = 100, blank = False)
    goodreads = models.URLField(max_length = 128, blank = True)
    headquote = models.CharField(max_length = 255)
    headline = models.CharField(max_length=128)
    quotes = RichTextField(blank = False)
    takeaways = RichTextField(blank = False)
    summary = RichTextField(blank = False)
    body = RichTextUploadingField(blank = False)
    resources = RichTextField(blank = False)
    dateCreated = models.DateTimeField(auto_now_add = True)
    dateUpdated = models.DateTimeField(auto_now = True)
    public = models.BooleanField(default = False)

    #RATINGS
    One = 'Not recommended'
    Two = 'Not recommended'
    Three = 'Good read'
    Four = 'Worth reading'
    Five = 'Must read'
    RATING_CHOICES = [
        (One, 'Bad'),
        (Two, 'Okay'),
        (Three,'Good'),
        (Four,'Great'),
        (Five,'Excellent')
    ]
    rating = models.CharField(max_length = 15, choices = RATING_CHOICES, default = Three)

    def __str__(self):
        return str(self.title)
    
    def save(self, *args, **kwargs):
        image_resize(self.cover, 625, 1000)
        super().save(*args, **kwargs)