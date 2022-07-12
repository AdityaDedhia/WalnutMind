from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.wikiView, name = "wikiindex"),
    path('define-<slug:pk_slug>', views.definitionView.as_view(), name = "definition"),
    path('lists', views.listsView, name = "listsview"),
    path('lists/new', views.newListView, name = "newlist"),
    path('lists/<slug:pk_slug>', views.listView.as_view(), name = "listview"),
    path('resource-<int:pk>',views.resourceView, name = "resourceview"),
    path('resources/', views.resourceList.as_view(), name = "resource-list"),
    path('collections', views.collectionsView, name = "collectionsview"),
    path('collections/<slug:pk_slug>', views.collectionView.as_view(), name = "collectionview"),
    path('topics/<tag>', views.tagView, name = "tagview"),
    path('search', views.searchView, name = "search"),
    path('terms/new', views.newTermView, name = "newterm"),
    path('resources/new', views.newResourceView, name = "newresource"),
    path('autocompleteterm/',views.TermAutoComplete.as_view(), name = "autocompleteterm"),
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

htmx_urlpatterns = [
    path('add-resource/', views.addResourceView, name = "add-resource"),
    path('delete-resource/<int:pk>', views.deleteResourceView, name = "delete-resource"),


]

urlpatterns += htmx_urlpatterns