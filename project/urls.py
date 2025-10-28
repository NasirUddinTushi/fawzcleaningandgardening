from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from apps.serviceapp.views import unread_count_api  # 
from apps.serviceapp.utils import get_quote_request

urlpatterns = [
    path('admin/api/unread-count/', unread_count_api, name='admin_unread_count_api'),  
    path('admin/', admin.site.urls),
    path('', include('apps.serviceapp.urls')),
    path("get-quote-request/<int:pk>/", get_quote_request, name="get_quote_request"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
