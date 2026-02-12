from django.urls import path

from . import views

app_name = "admin_portal"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<str:app_label>/<str:model_name>/", views.model_list, name="model_list"),
    path("<str:app_label>/<str:model_name>/new/", views.model_create, name="model_create"),
    path("<str:app_label>/<str:model_name>/<int:pk>/edit/", views.model_edit, name="model_edit"),
    path("<str:app_label>/<str:model_name>/<int:pk>/delete/", views.model_delete, name="model_delete"),
]
