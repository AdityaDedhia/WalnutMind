from django.contrib import admin

from .models import Profile
from .models import Highlight
from .models import Blacklist

admin.site.register(Profile)
admin.site.register(Highlight)

@admin.register(Blacklist)
class FileAdmin(admin.ModelAdmin):
    list_display = ['ip','datelog','reason']