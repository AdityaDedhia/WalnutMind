from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import searchView, articleView, updatePostView, articleupvote, articledownvote, newCommentView
 
urlpatterns = [
    path('', views.indexView, name = 'index'),
    path('articles',searchView.as_view(), name = 'articleindex'),
    path('articles/new', views.newPostView, name = 'newpost'),

    #if pk recieved, reroute to slug article url
    path('articles/<slug:pk_slug>', articleView.as_view(), name = 'articleview'),

    path('article-list',views.ArticleListAPIView.as_view(), name = 'article-list'),

    path('articles/<int:pk>/edit', updatePostView.as_view(), name = 'updatepost'),
    path('articles/<int:pk>/delete',views.deletePostView.as_view(), name = 'deletepost'),
    path('articles/<int:pk>/post',newCommentView, name = "newcomment"),

    path('articles/<int:pk>/upvote', articleupvote, name = 'article_upvote'),
    path('articles/<int:pk>/upvote', articledownvote, name = 'article_downvote'),

    path('about', views.aboutView, name = 'about'),
    path('opportunities', views.opportunitiesView, name = 'opportunities'),
    path('contact', views.contactView, name = 'contact'),
    path('roadmap', views.roadmapView, name = 'roadmap'),
    path('privacy_policy', views.privacyView, name = 'privacy'),
    path('end-user_agreement', views.termsView, name = 'terms'),
    path('faq', views.faqView, name = "faq"),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)