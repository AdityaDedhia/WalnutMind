from django.contrib import admin

from .models import Profile, Highlight, Blacklist, Log, Infraction, Subscriber

admin.site.register(Highlight)


@admin.register(Profile)
class FileAdmin(admin.ModelAdmin):
	search_fields = ['user__username']


@admin.register(Subscriber)
class FileAdmin(admin.ModelAdmin):
	search_fields = ['email', 'user__username']
	list_display = ['email', 'user', 'ip', 'dateCreated']


@admin.register(Blacklist)
class FileAdmin(admin.ModelAdmin):
	search_fields = ['ip']
	list_display = ['ip', 'datelog', 'reason']


@admin.register(Log)
class FileAdmin(admin.ModelAdmin):
	search_fields = ['description']
	list_display = ['user', 'datelog', 'description', 'link']


@admin.register(Infraction)
class FileAdmin(admin.ModelAdmin):
	search_fields = ['reason']
	list_display = ['user', 'datelog', 'reason']
