from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings


def home(request):
    if not settings.DEBUG:
        return HttpResponse(f'Hello, World! My name is {request.get_host()}. Im fine thank you')
    return HttpResponse(
        f'Welcome to PBS Image Playground backend API!<br>For documentation, go to '
        f'<a href="{reverse("api:schema-swagger-ui")}"> {reverse("api:schema-swagger-ui")}</a>'
    )