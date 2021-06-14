from django.urls import path
from django.conf import settings
from rest_framework import routers

from .views import processor
app_name = 'api'

urlpatterns = [
    path('png/tiff/', processor.Png2Tiff.as_view(), name='png2tiff'),
    path('png/eps/', processor.Png2Eps.as_view(), name='png2eps'),
    path('tiff/png/', processor.Tiff2Png.as_view(), name='tiff2png'),
    path('eps/png/', processor.Eps2Png.as_view(), name='eps2png'),
]



if settings.DEBUG:
    from django.urls import re_path
    from rest_framework.schemas import get_schema_view
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    schema_view = get_schema_view(
        openapi.Info(
            title="Snippets API",
            default_version='v1',
            description="Test description",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns.extend(
        [
            re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
            path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        ]
    )
