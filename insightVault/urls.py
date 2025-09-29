from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # accounts app URLs
    path('auth/', include('accounts.urls')),
    path('api/accounts/', include('accounts.api.urls')),

    # journal app URLs
    path('journal/', include('journal.urls')),
]

if settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
