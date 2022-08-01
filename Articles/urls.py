from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import article_save, updatePostView, deletePostView, \
	articleupvote, newCommentView, deleteCommentView, SearchView, ArticleView

urlpatterns = [
	              path('', views.index_view, name='index'),
	              path('articles', SearchView.as_view(), name='articleindex'),
	              path('articles/new', views.newPostView, name='newpost'),
	              path('articles/<int:pk>/post', newCommentView, name='newcomment'),
	              path('articles/<int:pk>/<int:id>/delete', deleteCommentView,
	                   name='deletecomment'),

	              # if pk recieved, reroute to slug article url
	              path('articles/<slug:pk_slug>', ArticleView.as_view(), name='articleview'),

	              path('article-list', views.ArticleListAPIView.as_view(), name='article-list'),
	              path('articles/<int:pk>/edit', updatePostView.as_view(), name='updatearticle'),
	              path('articles/<int:pk>/delete', deletePostView.as_view(), name='deletearticle'),

	              path('articles/<int:pk>/upvote', articleupvote, name='article_upvote'),
	              path('articles/<int:pk>/save', article_save, name='article_save'),

	              path('subscribe', views.subscribe_view, name='subscribe'),
	              path('about', views.about_view, name='about'),
	              path('opportunities', views.opportunities_view, name='opportunities'),
	              path('contact', views.contact_view, name='contact'),
	              path('roadmap', views.roadmap_view, name='roadmap'),
	              path('privacy-policy', views.privacy_view, name='privacy'),
	              path('end-user-agreement/', views.terms_view, name='terms'),
	              path('faq', views.faq_view, name="faq"),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
