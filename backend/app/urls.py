from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
#from api.v1.views import RedocView
from rest_framework.schemas import get_schema_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # path(
    #     'redoc/',
    #     TemplateView.as_view(template_name='redoc.html'),
    #     name='redoc'
    # ),
    # path('openapi', get_schema_view(
    #     title="Your Project",
    #     description="API for all things …",
    #     version="1.0.0"
    # ), name='openapi-schema'),
    # path('redoc/', RedocView.as_view()),
]
# schema_view = get_schema_view(
#     title='Server Monitoring API',
#     url='http://127.0.0.1:8000/redoc/',
#     patterns=urlpatterns,
#)