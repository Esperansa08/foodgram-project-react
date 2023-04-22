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
    path('redoc/openapi-schema.yml', get_schema_view(
        title="Foodgram",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
    path('redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc' ),

    # path('redoc/', RedocView.as_view()),
    # path('redoc/', TemplateView.as_view(
    #     template_name='redoc.html',
    #     extra_context={'schema_url':'openapi-schema'}
    # ), name='openapi-schema'),
    # ReDoc - другое использование и отображение созданной спецификации

]
# schema_view = get_schema_view(
#     title='Server Monitoring API',
#     url='http://127.0.0.1:8000/redoc/',
#     patterns=urlpatterns,
#)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)