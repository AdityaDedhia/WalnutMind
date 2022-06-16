from django.contrib import admin
from .models import Term, List, Resource, Collection
from django import forms


@admin.register(Term)
class FileAdmin(admin.ModelAdmin):
    list_display = ['term', 'definition']

    readonly_fields = ['slug']

admin.site.register(List)

admin.site.register(Resource)

admin.site.register(Collection)
