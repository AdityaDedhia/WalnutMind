from django.urls import path, reverse_lazy
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register',views.registerView, name = "registerr"),
    path('activate-user/<uidb64>/<token>',views.activate_user, name = 'activate'),
    path('login',views.loginView, name = "loginn"),
    path('logout', views.logoutView, name = 'logoutt'),
    path('<str:username>/', views.profileView, name = "profile"),
    path('<str:username>/edit', views.editProfileView, name = 'editprofile'),

    #PASSWORD MANAGEMENT URLS
    path('password/', auth_views.PasswordChangeView.as_view(template_name = 'Users/change-password.html', success_url = reverse_lazy('index')), name = "update_password"),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name = 'Users/password-reset.html'), name = "reset_password"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name = 'Users/reset-sent.html'), name = "password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = 'Users/change-password.html'), name = "password_reset_confirm"),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name = 'Users/reset-success.html'), name = "password_reset_complete"),
  
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
