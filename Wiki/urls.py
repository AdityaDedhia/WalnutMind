from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import definitionView, wikiView

urlpatterns = [
    path('',wikiView.as_view(), name = "wikiindex"),
    path('define-<slug:pk_slug>', definitionView.as_view(), name = "definition"),
    path('search-term', views.searchView, name = "searchterm"),
    path('terms/new', views.newTermView, name = "newterm"),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)