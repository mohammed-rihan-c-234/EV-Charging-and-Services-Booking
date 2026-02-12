"""Project URLs for EV Service."""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "EV Service Administration"
admin.site.site_title = "EV Service Admin"
admin.site.index_title = "Dashboard"

# simple home view to keep things clear for non-technical users
@login_required
def home(request):
    if getattr(request.user, "is_staff", False):
        return redirect("admin_portal:dashboard")
    try:
        if getattr(request.user.profile, "role", "") == "service_center":  # type: ignore[attr-defined]
            return redirect("service_center:dashboard")
    except Exception:
        pass

    from vehicles.models import Vehicle
    from bookings.models import ServiceBooking

    profile_name = ""
    try:
        profile_name = request.user.profile.full_name  # type: ignore[attr-defined]
    except Exception:
        profile_name = ""

    vehicles = Vehicle.objects.filter(
        Q(owner=request.user)
        | Q(owner_name=request.user.username)
        | (Q(owner_name=profile_name) if profile_name else Q(pk__in=[]))
    )

    pending_services = ServiceBooking.objects.filter(
        user=request.user,
        status__in=[ServiceBooking.STATUS_PENDING, ServiceBooking.STATUS_CONFIRMED],
        scheduled_for__gte=timezone.now() - timezone.timedelta(hours=1),
    ).select_related("service_center", "service_type")

    return render(
        request,
        "home_new.html",
        {"vehicles": vehicles, "pending_services": pending_services},
    )

def root(request):
    if request.user.is_authenticated:
        if getattr(request.user, "is_staff", False):
            return redirect("admin_portal:dashboard")
        try:
            if getattr(request.user.profile, "role", "") == "service_center":  # type: ignore[attr-defined]
                return redirect("service_center:dashboard")
        except Exception:
            pass
        return redirect("home")
    # Show public home page for non-authenticated users
    return render(request, "home_new.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-portal/', include('admin_portal.urls')),
    path('', root, name='root'),
    path('home/', home, name='home'),
    path('dashboard/', home, name='dashboard'),
    
    # Public pages
    path('about/', TemplateView.as_view(template_name='public/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='public/contact.html'), name='contact'),
    
    # App URLs
    path('', include('accounts.urls')),
    path('vehicles/', include('vehicles.urls')),
    path('services/', include('services.urls')),
    path('sos/', include('sos.urls')),
    path('chat/', include('chatbox.urls')),
    path('chatbox/', include('chatbox.urls')),
    path('charging/', include('charging.urls')),
    path('service-centers/', include('service_center.urls')),
    path('parts/', include('spareparts.urls')),
    path('spareparts/', include('spareparts.urls')),
    path('rewards/', include('rewards.urls')),
    path('bookings/', include('bookings.urls')),
    path('map/', include('maps.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
