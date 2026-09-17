from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=False,
        ROOT_URLCONF=__name__,
        SECRET_KEY="lecture-only",
        ALLOWED_HOSTS=["testserver"],
    )
import django
from django.http import JsonResponse
from django.urls import path

django.setup()

def health(_request):
    return JsonResponse({"status": "ok"})
urlpatterns = [path("health/", health, name="health")]
