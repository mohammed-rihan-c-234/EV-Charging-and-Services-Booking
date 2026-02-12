from django.urls import path

from . import views


app_name = "maps"


urlpatterns = [
    path("", views.map_page, name="map"),
    path("api/nearby/", views.api_nearby, name="api_nearby"),
]

