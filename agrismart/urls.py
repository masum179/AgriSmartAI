"""
AgriSmart AI — Root URL Configuration
Routes requests to each application module.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # Django admin (built-in)
    path('django-admin/', admin.site.urls),

    # App routes
    path('', lambda request: redirect('accounts:login'), name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('detection/', include('detection.urls', namespace='detection')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('panel/', include('adminpanel.urls', namespace='adminpanel')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
