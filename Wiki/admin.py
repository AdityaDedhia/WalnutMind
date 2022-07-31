from django.contrib import admin
from .models import Term, List, Resource, Collection, CollectionOrder


@admin.register(Term)
class FileAdmin(admin.ModelAdmin):
    list_display = ['term', 'definition']
    search_fields = ['term']

    readonly_fields = ['slug']


@admin.register(List)
class FileAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['terms']

    readonly_fields = ['slug']


@admin.register(Resource)
class FileAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title', 'category', 'creator', 'dateCreated']

    readonly_fields = ['dateCreated']


@admin.register(Collection)
class FileAdmin(admin.ModelAdmin):
    list_display = ['creator', 'title', 'dateCreated']


@admin.register(CollectionOrder)
class FileAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'collection', 'order', 'dateCreated']
