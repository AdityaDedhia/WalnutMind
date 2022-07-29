from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

import debug_toolbar

#admin.site.__class__ = AdminSiteOTPRequired #ADMIN SITE MAY ONLY BE ACCESSED BY STAFF IF THEY HAVE MFA ENABLED

urlpatterns = [
    path('&mfHQp04wVAYsorpv9clIsPv0CDq4vEsfB&pdJd^h38T27^A0dsC1UH!54gx8h3dQ7U6p$3QgTyhp8!YrS7o9OFsIfl*eZ4dNxqGI$kq/', admin.site.urls),
    path('', include(tf_twilio_urls)),
    path('ckeditor', include('ckeditor_uploader.urls')),
    path('users/',include('Users.urls')),
    path('', include(tf_urls)),
    path('users/', include('django.contrib.auth.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('', include('Articles.urls')),
    path('books/', include('Commentaries.urls')),
    path('blogs/', include('Diaries.urls')),
    path('wiki/', include('Wiki.urls')),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
