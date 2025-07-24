"""
Simple URL configuration for research platform demo.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mayan.apps.research.urls.api_urls')),
    path('research/', include('mayan.apps.research.urls.urlpatterns')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 