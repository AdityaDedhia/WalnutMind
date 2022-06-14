from django.contrib import admin
from .models import Post

@admin.register(Post)
class FileAdmin(admin.ModelAdmin):

    readonly_fields = ['slug']
