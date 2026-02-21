from django.contrib.auth import views as auth_views, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import SignUpForm, ProfileEditForm, UserProfileEditForm
from .models import Profile


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and getattr(user, "is_staff", False):
            return reverse("admin_portal:dashboard")
        try:
            if user and user.is_authenticated and getattr(user.profile, "role", "") == "service_center":  # type: ignore[attr-defined]
                return reverse("service_center:dashboard")
        except Exception:
            pass
        return reverse("home")


@login_required
def profile_view(request):
    """Display user profile."""
    try:
        profile = request.user.profile  # type: ignore[attr-defined]
    except Profile.DoesNotExist:
        profile = None
    
    return render(request, "accounts/profile.html", {"profile": profile, "user": request.user})


@login_required
def profile_edit(request):
    try:
        profile = request.user.profile  # type: ignore[attr-defined]
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            phone_number="",
            role=Profile.ROLE_USER,
        )

    if request.method == "POST":
        user_form = UserProfileEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            updated_profile = profile_form.save(commit=False)
            if updated_profile.role == Profile.ROLE_SERVICE_CENTER:
                request.user.first_name = ""
                request.user.last_name = ""
            else:
                full_name = (updated_profile.full_name or "").strip()
                name_parts = full_name.split(" ", 1)
                request.user.first_name = name_parts[0] if name_parts else ""
                request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
            request.user.save(update_fields=["first_name", "last_name"])
            updated_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        user_form = UserProfileEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)

    return render(
        request,
        "accounts/profile_edit.html",
        {"profile_form": profile_form, "user_form": user_form},
    )


class CustomLogoutView(View):
    """Custom logout view that handles both GET and POST."""

    def get(self, request, *args, **kwargs):
        """Handle GET requests by logging out and redirecting to login."""
        logout(request)
        return redirect(reverse("accounts:login"))

    def post(self, request, *args, **kwargs):
        """Handle POST requests."""
        logout(request)
        return redirect(reverse("accounts:login"))
