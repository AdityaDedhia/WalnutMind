from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import booksView, bookView

urlpatterns = [
    path('',booksView.as_view(), name = 'bookindex'),
    path('new', views.newPostView, name = 'newbookpost'),
    path('<slug:pk_slug>/', bookView.as_view(), name = 'bookview'),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)