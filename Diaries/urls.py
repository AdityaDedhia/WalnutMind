from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from . import views
from .views import diariesView, diaryView

urlpatterns = [
    path('',diariesView.as_view(), name = 'blogindex'),
    path('new', views.newPostView, name = 'newblogpost'),
    path('<slug:pk_slug>', diaryView.as_view(), name = 'blogview'),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)