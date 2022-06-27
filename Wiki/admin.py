from django.contrib import admin
from .models import Term, List, Resource, Collection

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



@admin.register(Collection)
class FileAdmin(admin.ModelAdmin):
    search_fields = ['title']
    autocomplete_fields = ['resources']

    readonly_fields = ['slug']