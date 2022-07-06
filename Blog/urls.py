from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('&mfHQp04wVAYsorpv9clIsPv0CDq4vEsfB&pdJd^h38T27^A0dsC1UH!54gx8h3dQ7U6p$3QgTyhp8!YrS7o9OFsIfl*eZ4dNxqGI$kq/', admin.site.urls),
    path('ckeditor', include('ckeditor_uploader.urls')),
    path('users/',include('Users.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('', include('Articles.urls')),
    path('books/', include('Commentaries.urls')),
    path('blogs/', include('Diaries.urls')),
    path('wiki/', include('Wiki.urls')),
    path('polls/', include('Polls.urls')),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
