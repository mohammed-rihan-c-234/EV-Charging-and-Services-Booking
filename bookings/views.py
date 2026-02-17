from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.conf import settings
import razorpay

from accounts.models import Profile

from .forms import ServiceBookingForm, BookingPaymentForm
from .models import ServiceBooking
from rewards.models import Coupon
from rewards.utils import award_points
from vehicles.models import Vehicle


@login_required
def booking_create(request):
    initial = {}
    try:
        profile = request.user.profile  # type: ignore[attr-defined]
        initial = {"name": profile.full_name, "phone_number": profile.phone_number}
    except Profile.DoesNotExist:
        initial = {}

    if request.method == "POST":
        form = ServiceBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.amount = booking.service_type.base_price if booking.service_type_id else 0
            booking.save()
            return redirect("bookings:checkout", pk=booking.pk)
    else:
        form = ServiceBookingForm(initial=initial, user=request.user)

    user_vehicles = Vehicle.objects.for_user(request.user).order_by("make", "model")
    return render(request, "bookings/booking_form.html", {"form": form, "user_vehicles": user_vehicles})


@login_required
def my_bookings(request):
    qs = ServiceBooking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": qs})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        ServiceBooking.objects.select_related("service_type", "service_center", "vehicle"),
        pk=pk,
        user=request.user,
    )
    return render(request, "bookings/booking_detail.html", {"booking": booking})


@login_required
def booking_checkout(request, pk):
    booking = ServiceBooking.objects.select_related("service_type", "service_center").get(pk=pk, user=request.user)
    
    # Handle coupon application
    if request.method == "POST" and "apply_coupon" in request.POST:
        coupon_code = request.POST.get("coupon_code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            original_amount = booking.get_original_amount()
            discount_amount = (original_amount * Decimal(coupon.discount_percent)) / Decimal(100)
            booking.coupon_discount = discount_amount
            booking.amount = original_amount - discount_amount
            booking.save(update_fields=["coupon_discount", "amount"])
            messages.success(request, f"Coupon applied! You saved ₹{discount_amount:.2f}")
            return redirect("bookings:checkout", pk=booking.pk)
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            return redirect("bookings:checkout", pk=booking.pk)
    
    if request.method == "POST" and "remove_coupon" in request.POST:
        original_amount = booking.get_original_amount()
        booking.coupon_discount = Decimal("0.00")
        booking.amount = original_amount
        booking.save(update_fields=["coupon_discount", "amount"])
        messages.info(request, "Coupon removed.")
        return redirect("bookings:checkout", pk=booking.pk)
    
    if request.method == "POST" and "payment_method" in request.POST:
        form = BookingPaymentForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data["payment_method"]
            booking.payment_method = method
            if method == ServiceBooking.PAYMENT_METHOD_RAZORPAY:
                booking.save(update_fields=["payment_method"])
                return redirect("bookings:razorpay_payment", pk=booking.pk)
            booking.payment_status = ServiceBooking.PAYMENT_PENDING_CASH
            booking.save(update_fields=["payment_method", "payment_status"])
            
            # Award reward points
            points_awarded = award_points(request.user, booking.amount, "Service booking")
            if points_awarded > 0:
                messages.success(request, f"Payment recorded. You earned {points_awarded} reward points!")
            else:
                messages.success(request, "Payment recorded.")
            return redirect("bookings:my_bookings")
    else:
        form = BookingPaymentForm()

    coupons = Coupon.objects.filter(active=True)
    return render(request, "bookings/booking_checkout.html", {"booking": booking, "form": form, "available_coupons": coupons})


@login_required
def razorpay_payment(request, pk):
    booking = ServiceBooking.objects.select_related("service_type", "service_center").get(pk=pk, user=request.user)
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Razorpay keys are not configured. Please add test keys to continue.")
        return redirect("bookings:checkout", pk=booking.pk)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_display = Decimal(booking.amount).quantize(Decimal("0.01"))
    amount_paise = int(amount_display * 100)
    rp_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"booking_{booking.pk}",
        "payment_capture": 1,
    })
    booking.razorpay_order_id = rp_order.get("id", "")
    booking.save(update_fields=["razorpay_order_id"])

    return render(
        request,
        "bookings/razorpay_payment.html",
        {
            "booking": booking,
            "amount_display": amount_display,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": booking.razorpay_order_id,
            "amount_paise": amount_paise,
        },
    )


@login_required
def razorpay_verify(request, pk):
    booking = ServiceBooking.objects.select_related("service_type", "service_center").get(pk=pk, user=request.user)
    if request.method != "POST":
        return redirect("bookings:razorpay_payment", pk=pk)
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Razorpay keys are not configured.")
        return redirect("bookings:checkout", pk=booking.pk)

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
        return redirect("bookings:razorpay_payment", pk=pk)

    booking.payment_method = ServiceBooking.PAYMENT_METHOD_RAZORPAY
    booking.payment_status = ServiceBooking.PAYMENT_PAID
    booking.razorpay_order_id = order_id
    booking.razorpay_payment_id = payment_id
    booking.save(update_fields=["payment_method", "payment_status", "razorpay_order_id", "razorpay_payment_id"])
    points_awarded = award_points(request.user, booking.amount, "Service booking")
    if points_awarded > 0:
        messages.success(request, f"Payment successful. You earned {points_awarded} reward points!")
    else:
        messages.success(request, "Payment successful.")
    return redirect("bookings:my_bookings")

# Create your views here.
