import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views
from django.urls import path, include
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls
from two_factor.urls import urlpatterns as tf_urls

import Blog.sitemaps as site_categories

# admin.site.__class__ = AdminSiteOTPRequired  # Admin site requires MFA enabled in profile

sitemaps = {
	'static': site_categories.StaticSitemap,
	'articles': site_categories.ArticleSitemap,
	'commentaries': site_categories.CommentarySitemap,
	'blogs': site_categories.DiarySitemap,
}

urlpatterns = [
	              path(
		              '&mfHQp04wVAYsorpv9clIsPv0CDq4vEsfB&pdJd^h38T27^A0dsC1UH!54gx8h3dQ7U6p$3QgTyhp8'
		              '!YrS7o9OFsIfl*eZ4dNxqGI$kq/', admin.site.urls),
	              path('', include(tf_twilio_urls)),
	              path('ckeditor', include('ckeditor_uploader.urls')),
	              path('users/', include('Users.urls')),
	              path('', include(tf_urls)),
	              path('users/', include('django.contrib.auth.urls')),
	              path('__debug__/', include(debug_toolbar.urls)),

	              path('sitemap.xml', views.index, {'sitemaps': sitemaps},
	                   name='django.contrib.sitemaps.views.sitemap'),
	              path('sitemap-<section>.xml', views.sitemap, {'sitemaps': sitemaps},
	                   name='django.contrib.sitemaps.views.sitemap'),

	              path('', include('Articles.urls')),
	              path('books/', include('Commentaries.urls')),
	              path('blogs/', include('Diaries.urls')),
	              path('wiki/', include('Wiki.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
