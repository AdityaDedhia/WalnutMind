from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import diaryView, updatePostView, diaryupvote, diarysave,\
    newCommentView, deleteCommentView

urlpatterns = [
    path('', views.diariesView, name='blogindex'),
    path('new', views.newPostView, name='newblogpost'),
    path('<str:username>/<slug:pk_slug>', diaryView.as_view(), name='blogview'),
    path('<str:username>/<int:pk>/edit', updatePostView.as_view(), name='updateblog'),

    path('<str:username>/<int:pk>/upvote', diaryupvote, name='diary_upvote'),
    path('<str:username>/<int:pk>/save', diarysave, name='diary_save'),

    path('<str:username>/<int:pk>/post', newCommentView, name='newdiarycomment'),
    path('<str:username>/<int:pk>/<int:id>/delete', deleteCommentView, name="deletediarycomment"),

    path('profile-list', views.ProfileListAPIView.as_view(), name='profile-list'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
