from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField

class Term(models.Model):
    term = models.CharField(max_length=128, blank = False)
    slug = AutoSlugField(populate_from='term', unique = True, null = True, default = None)
    definition = RichTextUploadingField(blank = False)
    dateUpdated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return str(self.term)