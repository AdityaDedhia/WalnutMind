from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import definitionView, collectionView, listView, TermAutoComplete

urlpatterns = [
    path('',views.wikiView, name = "wikiindex"),
    path('define-<slug:pk_slug>', definitionView.as_view(), name = "definition"),
    path('lists', views.listsView, name = "listsview"),
    path('lists/new', views.newListView, name = "newlist"),
    path('lists/<slug:pk_slug>', listView.as_view(), name = "listview"),
    path('resource-<int:pk>',views.resourceView, name = "resourceview"),
    path('collections', views.collectionsView, name = "collectionsview"),
    path('collections/<slug:pk_slug>', collectionView.as_view(), name = "collectionview"),
    path('topics/<tag>', views.tagView, name = "tagview"),
    path('search', views.searchView, name = "search"),
    path('terms/new', views.newTermView, name = "newterm"),
    path('resources/new', views.newResourceView, name = "newresource"),
    path('autocompleteterm/',TermAutoComplete.as_view(), name = "autocompleteterm"),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)