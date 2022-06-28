from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE, DO_NOTHING
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
from Blog.utils import image_resize
from taggit.managers import TaggableManager
from django.urls import reverse


class Post(models.Model):
    title = models.CharField(max_length=128, blank = False) #Blank=false for required fields
    slug = AutoSlugField(populate_from='title', unique = True, null = True, default = None)
    tags = TaggableManager(related_name="commentarytags")
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentarypublisher")
    author = models.CharField(max_length = 50, blank = False)
    isbn = models.CharField(null = True, blank = True, max_length=13)
    year = models.IntegerField(blank=False)
    pages = models.IntegerField()
    cover = models.ImageField(upload_to = 'Commentaries/commentary_covers', blank = False)
    headquote = models.CharField(max_length = 255)
    abstract = models.CharField(max_length=128)
    quotes = models.TextField(blank = False)
    takeaways = models.TextField(max_length = 500, blank = False)
    summary = models.TextField(max_length = 1500, blank = False)
    content = RichTextUploadingField(blank = False)
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
    
    def get_absolute_url(self):
        return reverse('bookview', kwargs={'pk_slug': str(self.slug)})
    
    def save(self, *args, **kwargs):
        image_resize(self.cover, 625, 1000)
        super().save(*args, **kwargs)