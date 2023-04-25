from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
#from api.v1.views import RedocView
from drf_yasg import openapi
#from drf_yasg.views import get_schema_view
from rest_framework.schemas import get_schema_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)