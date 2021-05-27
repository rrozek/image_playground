from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings


def home(request):
    if not settings.DEBUG:
        return HttpResponse('Hello, World! Im fine thank you')
    return HttpResponse(
        f'Hello, World!<br>For api documentation, go to '
        f'<a href="{reverse("api:schema-swagger-ui")}"> {reverse("api:schema-swagger-ui")}</a>')
