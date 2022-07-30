from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class FileAdmin(admin.ModelAdmin):

    readonly_fields = ['slug']


admin.site.register(Comment)
