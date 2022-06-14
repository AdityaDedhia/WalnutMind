from django.contrib import admin
from .models import Term

@admin.register(Term)
class FileAdmin(admin.ModelAdmin):
    list_display = ['term', 'definition']

    readonly_fields = ['slug']