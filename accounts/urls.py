from django.urls import path
from django.contrib.auth import views as auth_views

from .views import LoginView, SignUpView, profile_view, profile_edit, CustomLogoutView


app_name = "accounts"


urlpatterns = [
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        CustomLogoutView.as_view(),
        name="logout",
    ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
]
