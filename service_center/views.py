from django.shortcuts import render
from .models import ServiceCenter
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone

from bookings.models import ServiceBooking
from chatbox.models import ChatMessage, ChatSession
from spareparts.models import PartOrder
from rewards.utils import award_points

def center_list(request):
    centers = ServiceCenter.objects.all()
    return render(request, 'service_center/center_list.html', {'centers': centers})


def api_centers(request):
    qs = ServiceCenter.objects.all()
    data = []
    for c in qs:
        data.append({
            'id': c.id,
            'name': c.name,
            'address': c.address,
            'latitude': c.latitude,
            'longitude': c.longitude,
            'phone': c.phone,
        })
    return JsonResponse({'service_centers': data})


@login_required
@user_passes_test(
    lambda u: bool(
        getattr(u, "is_staff", False)
        or u.groups.filter(name="service_center").exists()
        or (hasattr(u, "profile") and getattr(getattr(u, "profile", None), "role", "") == "service_center")
    )
)
def dashboard(request):
    qs = ServiceBooking.objects.select_related("service_center", "service_type", "user")
    center_id = request.GET.get("center")
    centers = ServiceCenter.objects.all()
    if not request.user.is_staff:
        try:
            profile = request.user.profile  # type: ignore[attr-defined]
            if profile.service_center_id:
                center_id = str(profile.service_center_id)
                qs = qs.filter(service_center_id=profile.service_center_id)
                centers = ServiceCenter.objects.filter(id=profile.service_center_id)
            else:
                qs = qs.none()
                centers = ServiceCenter.objects.none()
        except Exception:
            qs = qs.none()
            centers = ServiceCenter.objects.none()
    else:
        if center_id:
            qs = qs.filter(service_center_id=center_id)

    last_msg = ChatMessage.objects.filter(session=OuterRef("pk")).order_by("-created_at")
    chat_sessions_qs = ChatSession.objects.select_related("user", "service_center")
    if not request.user.is_staff:
        try:
            profile = request.user.profile  # type: ignore[attr-defined]
            if profile.service_center_id:
                chat_sessions_qs = chat_sessions_qs.filter(service_center_id=profile.service_center_id)
            else:
                chat_sessions_qs = chat_sessions_qs.none()
        except Exception:
            chat_sessions_qs = chat_sessions_qs.none()
    elif center_id:
        chat_sessions_qs = chat_sessions_qs.filter(service_center_id=center_id)

    chat_sessions = (
        chat_sessions_qs
        .annotate(last_text=Subquery(last_msg.values("text")[:1]))
        .annotate(last_time=Subquery(last_msg.values("created_at")[:1]))
        .order_by("-last_time", "-created_at")[:25]
    )

    show = (request.GET.get("show") or "pending").strip().lower()

    bookings_paid = qs.exclude(payment_status=ServiceBooking.PAYMENT_UNPAID)
    bookings_pending = bookings_paid.filter(approval_status=ServiceBooking.APPROVAL_PENDING).order_by(
        "scheduled_for", "-created_at"
    )
    bookings_all = bookings_paid.order_by("-scheduled_for", "-created_at")

    part_orders_qs = (
        PartOrder.objects.select_related("user", "service_center")
        .prefetch_related("items", "items__part")
        .exclude(status=PartOrder.STATUS_CART)
        .exclude(payment_status=PartOrder.PAYMENT_UNPAID)
        .order_by("-created_at")
    )
    if not request.user.is_staff:
        try:
            profile = request.user.profile  # type: ignore[attr-defined]
            if profile.service_center_id:
                part_orders_qs = part_orders_qs.filter(service_center_id=profile.service_center_id)
            else:
                part_orders_qs = part_orders_qs.none()
        except Exception:
            part_orders_qs = part_orders_qs.none()
    elif center_id:
        part_orders_qs = part_orders_qs.filter(service_center_id=center_id)
    part_orders_pending = part_orders_qs.filter(status=PartOrder.STATUS_PLACED)[:25]
    part_orders_all = part_orders_qs[:25]
    return render(
        request,
        "service_center/dashboard.html",
        {
            "show": show,
            "bookings_pending": bookings_pending,
            "bookings_all": bookings_all,
            "centers": centers,
            "selected_center": center_id or "",
            "chat_sessions": chat_sessions,
            "part_orders_pending": part_orders_pending,
            "part_orders_all": part_orders_all,
        },
    )


@login_required
@user_passes_test(
    lambda u: bool(
        getattr(u, "is_staff", False)
        or u.groups.filter(name="service_center").exists()
        or (hasattr(u, "profile") and getattr(getattr(u, "profile", None), "role", "") == "service_center")
    )
)
@require_POST
def booking_decide(request, pk):
    booking = get_object_or_404(ServiceBooking, pk=pk)
    action = request.POST.get("action")
    if action == "accept":
        booking.approval_status = ServiceBooking.APPROVAL_ACCEPTED
        booking.status = ServiceBooking.STATUS_CONFIRMED
        # Award reward points to the user when booking is accepted
        award_points(booking.user, booking.amount, "Service booking acceptance")
    elif action == "reject":
        booking.approval_status = ServiceBooking.APPROVAL_REJECTED
        booking.status = ServiceBooking.STATUS_CANCELED
    else:
        return redirect("service_center:dashboard")
    booking.decided_by = request.user
    booking.decided_at = timezone.now()
    booking.save(update_fields=["approval_status", "status", "decided_by", "decided_at"])
    return redirect("service_center:dashboard")


@login_required
@user_passes_test(
    lambda u: bool(
        getattr(u, "is_staff", False)
        or u.groups.filter(name="service_center").exists()
        or (hasattr(u, "profile") and getattr(getattr(u, "profile", None), "role", "") == "service_center")
    )
)
@require_POST
def order_decide(request, pk):
    order = get_object_or_404(PartOrder, pk=pk)
    action = request.POST.get("action")
    if action == "accept":
        order.status = PartOrder.STATUS_ACCEPTED
        # Award reward points to the user when order is accepted
        award_points(order.user, order.total_amount, "Spare parts order acceptance")
    elif action == "reject":
        order.status = PartOrder.STATUS_REJECTED
    else:
        return redirect("service_center:dashboard")
    order.decided_by = request.user
    order.decided_at = timezone.now()
    order.save(update_fields=["status", "decided_by", "decided_at"])
    return redirect("service_center:dashboard")
