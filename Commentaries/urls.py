from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import booksView, bookView, updatePostView, post_json

urlpatterns = [
    path('post-json/', post_json, name = 'post-json-view'),
    path('',booksView.as_view(), name = 'bookindex'),
    path('new', views.newPostView, name = 'newbookpost'),
    path('<int:pk>/edit', updatePostView.as_view(), name = 'updatebook'),
    path('<slug:pk_slug>/', bookView.as_view(), name = 'bookview'),
    path('book-list',views.BookListAPIView.as_view(), name = 'book-list'),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)