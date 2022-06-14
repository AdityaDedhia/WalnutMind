from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Articles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor', include('ckeditor_uploader.urls')),
    path('users/',include('Users.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('', include('Articles.urls')),
    path('books/', include('Commentaries.urls')),
    path('blogs/', include('Diaries.urls')),
    path('wiki/', include('Wiki.urls')),
    path('polls/', include('Polls.urls')),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
