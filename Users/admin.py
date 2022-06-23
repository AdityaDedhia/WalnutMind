from django.contrib import admin

from .models import Profile, Highlight, Blacklist, Log


admin.site.register(Profile)
admin.site.register(Highlight)

@admin.register(Blacklist)
class FileAdmin(admin.ModelAdmin):
    list_display = ['ip','datelog','reason']

@admin.register(Log)
class FileAdmin(admin.ModelAdmin):
    list_display = ['user','datelog','description','link']