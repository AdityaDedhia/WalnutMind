from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class FileAdmin(admin.ModelAdmin):
    list_display = ['title','author','dateCreated','get_tags']

    def get_tags(self,obj):
        return ", ".join(x for x in obj.tags.names())

    def get_queryset(self,request):
        return super().get_queryset(request).prefetch_related('tags')

    readonly_fields = ['slug']


admin.site.register(Comment)