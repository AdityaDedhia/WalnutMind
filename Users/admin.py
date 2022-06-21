from django.contrib import admin

from .models import Profile
from .models import Highlight

admin.site.register(Profile)
admin.site.register(Highlight)