from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
import razorpay
from .models import ChargingStation, ChargingBooking
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from rewards.utils import award_points
from rewards.models import RewardAccount


def station_list(request):
    stations = ChargingStation.objects.all()
    return render(request, 'charging/station_list.html', {'stations': stations})


def api_stations(request):
    """Return JSON list of charging stations with basic availability info."""
    qs = ChargingStation.objects.all()
    data = []
    for s in qs:
        data.append({
            'id': s.id,
            'name': s.name,
            'latitude': s.latitude,
            'longitude': s.longitude,
            'available_slots': s.available_slots,
            'plug_types': s.plug_types,
        })
    return JsonResponse({'stations': data})


@login_required
def book_charging(request, station_id):
    """Book a charging session at a station."""
    station = get_object_or_404(ChargingStation, pk=station_id)

    if request.method == 'POST':
        duration_hours = int(request.POST.get('duration', 2) or 2)
        notes = (request.POST.get("notes") or "").strip()
        scheduled_date_input = (request.POST.get("scheduled_date") or "").strip()
        scheduled_time_input = (request.POST.get("scheduled_time") or "").strip()
        scheduled_at_input = (request.POST.get("scheduled_at") or "").strip()

        scheduled_at = None
        if scheduled_date_input and scheduled_time_input:
            parsed_date = parse_date(scheduled_date_input)
            parsed_time = parse_time(scheduled_time_input)
            if parsed_date and parsed_time:
                combined_dt = timezone.datetime.combine(parsed_date, parsed_time)
                scheduled_at = timezone.make_aware(combined_dt, timezone.get_current_timezone())
        elif scheduled_at_input:
            parsed_dt = parse_datetime(scheduled_at_input)
            if parsed_dt:
                if timezone.is_naive(parsed_dt):
                    scheduled_at = timezone.make_aware(parsed_dt, timezone.get_current_timezone())
                else:
                    scheduled_at = parsed_dt

        if not scheduled_at:
            messages.error(request, "Please choose a valid charging date and time.")
            return render(
                request,
                'charging/book_station.html',
                {
                    'station': station,
                    'duration': duration_hours,
                    'scheduled_date': scheduled_date_input,
                    'scheduled_time': scheduled_time_input,
                    'notes': notes,
                },
            )
        if scheduled_at <= timezone.now():
            messages.error(request, "Charging date and time must be in the future.")
            return render(
                request,
                'charging/book_station.html',
                {
                    'station': station,
                    'duration': duration_hours,
                    'scheduled_date': scheduled_date_input,
                    'scheduled_time': scheduled_time_input,
                    'notes': notes,
                },
            )
        
        # Create charging booking
        booking = ChargingBooking.objects.create(
            user=request.user,
            station=station,
            duration_hours=duration_hours,
            scheduled_at=scheduled_at,
            amount=duration_hours * station.price_per_hour,
            status=ChargingBooking.STATUS_PENDING,
            payment_status=ChargingBooking.PAYMENT_UNPAID
        )

        return redirect('charging:razorpay_payment', booking_id=booking.id)
    
    return render(request, 'charging/book_station.html', {'station': station})


@login_required
def booking_confirmation(request, booking_id):
    """Show booking confirmation with map."""
    booking = get_object_or_404(ChargingBooking, pk=booking_id, user=request.user)
    all_stations = ChargingStation.objects.all()
    
    return render(request, 'charging/booking_confirmation.html', {
        'booking': booking,
        'station': booking.station,
        'stations': all_stations
    })


@login_required
def my_charging_bookings(request):
    bookings = ChargingBooking.objects.select_related("station").filter(user=request.user)
    return render(request, "charging/my_bookings.html", {"bookings": bookings})


@login_required
def razorpay_payment(request, booking_id):
    booking = ChargingBooking.objects.select_related("station").get(pk=booking_id, user=request.user)
    if booking.payment_status == ChargingBooking.PAYMENT_PAID:
        return redirect("charging:booking_confirmation", booking_id=booking.pk)
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Razorpay keys are not configured. Please add test keys to continue.")
        return redirect("charging:my_bookings")

    if request.method == "POST" and "apply_points" in request.POST:
        requested_points = int(request.POST.get("points_to_use", "0") or 0)
        reward_account = RewardAccount.objects.filter(user=request.user).first()
        available_points = reward_account.points if reward_account else 0
        payable_amount = Decimal(booking.amount)
        max_points_by_amount = int((payable_amount * Decimal("10")).to_integral_value())
        max_points = min(available_points, max_points_by_amount)
        points_to_apply = max(0, min(requested_points, max_points))
        booking.points_redeemed = points_to_apply
        booking.points_discount = (Decimal(points_to_apply) / Decimal("10")).quantize(Decimal("0.01"))
        booking.save(update_fields=["points_redeemed", "points_discount"])
        if points_to_apply > 0:
            messages.success(request, f"Applied {points_to_apply} reward points.")
        else:
            messages.info(request, "No reward points applied.")
        return redirect("charging:razorpay_payment", booking_id=booking.pk)

    if request.method == "POST" and "remove_points" in request.POST:
        booking.points_redeemed = 0
        booking.points_discount = Decimal("0.00")
        booking.save(update_fields=["points_redeemed", "points_discount"])
        messages.info(request, "Reward points removed.")
        return redirect("charging:razorpay_payment", booking_id=booking.pk)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payable_amount = Decimal(booking.amount) - Decimal(booking.points_discount or 0)
    if payable_amount < Decimal("0.00"):
        payable_amount = Decimal("0.00")
    amount_display = payable_amount.quantize(Decimal("0.01"))
    amount_paise = int(amount_display * 100)
    rp_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"charging_{booking.pk}",
        "payment_capture": 1,
    })
    booking.razorpay_order_id = rp_order.get("id", "")
    booking.save(update_fields=["razorpay_order_id"])

    reward_account = RewardAccount.objects.filter(user=request.user).first()
    available_points = reward_account.points if reward_account else 0

    return render(
        request,
        "charging/razorpay_payment.html",
        {
            "booking": booking,
            "amount_display": amount_display,
            "available_points": available_points,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": booking.razorpay_order_id,
            "amount_paise": amount_paise,
        },
    )


@login_required
def razorpay_verify(request, booking_id):
    booking = ChargingBooking.objects.select_related("station").get(pk=booking_id, user=request.user)
    if request.method != "POST":
        return redirect("charging:razorpay_payment", booking_id=booking_id)
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Razorpay keys are not configured.")
        return redirect("charging:my_bookings")

    payment_id = request.POST.get("razorpay_payment_id", "")
    order_id = request.POST.get("razorpay_order_id", "")
    signature = request.POST.get("razorpay_signature", "")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment verification failed. Please try again.")
        return redirect("charging:razorpay_payment", booking_id=booking_id)

    booking.payment_method = ChargingBooking.PAYMENT_METHOD_RAZORPAY
    booking.payment_status = ChargingBooking.PAYMENT_PAID
    booking.status = ChargingBooking.STATUS_CONFIRMED
    booking.razorpay_order_id = order_id
    booking.razorpay_payment_id = payment_id
    booking.save(update_fields=["payment_method", "payment_status", "status", "razorpay_order_id", "razorpay_payment_id"])

    if booking.points_redeemed > 0:
        reward_account = RewardAccount.objects.filter(user=request.user).first()
        if reward_account:
            points_used = min(reward_account.points, booking.points_redeemed)
            reward_account.points -= points_used
            reward_account.save(update_fields=["points"])
            if points_used != booking.points_redeemed:
                booking.points_redeemed = points_used
                booking.points_discount = (Decimal(points_used) / Decimal("10")).quantize(Decimal("0.01"))
                booking.save(update_fields=["points_redeemed", "points_discount"])

    payable_amount = Decimal(booking.amount) - Decimal(booking.points_discount or 0)
    if payable_amount < Decimal("0.00"):
        payable_amount = Decimal("0.00")
    points_awarded = award_points(request.user, payable_amount, "Charging booking")
    if points_awarded > 0:
        messages.success(request, f"Payment successful. You earned {points_awarded} reward points!")
    else:
        messages.success(request, "Payment successful.")

    return redirect("charging:booking_confirmation", booking_id=booking.pk)
