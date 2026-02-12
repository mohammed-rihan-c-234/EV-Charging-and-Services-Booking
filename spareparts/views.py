from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from decimal import Decimal
from django.conf import settings

from .forms import PaymentChoiceForm
from .models import SparePart, PartOrder, PartOrderItem
from django.http import JsonResponse
from rewards.models import Coupon
from rewards.utils import award_points
from rewards.models import RewardAccount
import razorpay

def parts_list(request):
    parts = SparePart.objects.all()
    return render(request, 'spareparts/parts_list.html', {'parts': parts})


def part_detail(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    return render(request, "spareparts/part_detail.html", {"part": part})


def _get_cart(user):
    cart, _ = PartOrder.objects.get_or_create(user=user, status=PartOrder.STATUS_CART)
    return cart


@login_required
def cart_detail(request):
    cart = _get_cart(request.user)
    cart.recalc_total()
    return render(request, "spareparts/cart.html", {"cart": cart})


@login_required
def cart_add(request, pk):
    part = get_object_or_404(SparePart, pk=pk)
    cart = _get_cart(request.user)
    item, created = PartOrderItem.objects.get_or_create(
        order=cart, part=part, defaults={"quantity": 1, "unit_price": part.price}
    )
    if not created:
        item.quantity += 1
        item.save(update_fields=["quantity"])
    cart.recalc_total()
    messages.success(request, f"Added {part.name} to cart.")
    return redirect("spareparts:cart")


@login_required
def cart_remove(request, item_id):
    cart = _get_cart(request.user)
    item = get_object_or_404(PartOrderItem, pk=item_id, order=cart)
    item.delete()
    cart.recalc_total()
    return redirect("spareparts:cart")


@login_required
def cart_update(request, item_id):
    cart = _get_cart(request.user)
    item = get_object_or_404(PartOrderItem, pk=item_id, order=cart)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "inc":
            item.quantity += 1
            item.save(update_fields=["quantity"])
        elif action == "dec":
            if item.quantity <= 1:
                item.delete()
            else:
                item.quantity -= 1
                item.save(update_fields=["quantity"])
    cart.recalc_total()
    return redirect("spareparts:cart")


@login_required
def cart_checkout(request):
    cart = _get_cart(request.user)
    if not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("spareparts:list")

    cart.recalc_total()
    
    # Handle coupon application
    if request.method == "POST" and "apply_coupon" in request.POST:
        coupon_code = request.POST.get("coupon_code", "").strip().upper()
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            original_total = cart.get_original_total()
            discount_amount = (original_total * Decimal(coupon.discount_percent)) / Decimal(100)
            cart.coupon_discount = discount_amount
            cart.save(update_fields=["coupon_discount"])
            cart.recalc_total()
            messages.success(request, f"Coupon applied! You saved ₹{discount_amount:.2f}")
            return redirect("spareparts:checkout")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            return redirect("spareparts:checkout")
    
    if request.method == "POST" and "remove_coupon" in request.POST:
        cart.coupon_discount = Decimal("0.00")
        cart.save(update_fields=["coupon_discount"])
        cart.recalc_total()
        messages.info(request, "Coupon removed.")
        return redirect("spareparts:checkout")

    if request.method == "POST" and "apply_points" in request.POST:
        requested_points = int(request.POST.get("points_to_use", "0") or 0)
        reward_account = RewardAccount.objects.filter(user=request.user).first()
        available_points = reward_account.points if reward_account else 0
        base_amount = Decimal(cart.get_original_total()) - Decimal(cart.coupon_discount or 0)
        if base_amount < Decimal("0.00"):
            base_amount = Decimal("0.00")
        max_points_by_amount = int((base_amount * Decimal("10")).to_integral_value())
        max_points = min(available_points, max_points_by_amount)
        points_to_apply = max(0, min(requested_points, max_points))
        cart.points_redeemed = points_to_apply
        cart.points_discount = (Decimal(points_to_apply) / Decimal("10")).quantize(Decimal("0.01"))
        cart.save(update_fields=["points_redeemed", "points_discount"])
        cart.recalc_total()
        if points_to_apply > 0:
            messages.success(request, f"Applied {points_to_apply} reward points.")
        else:
            messages.info(request, "No reward points applied.")
        return redirect("spareparts:checkout")

    if request.method == "POST" and "remove_points" in request.POST:
        cart.points_redeemed = 0
        cart.points_discount = Decimal("0.00")
        cart.save(update_fields=["points_redeemed", "points_discount"])
        cart.recalc_total()
        messages.info(request, "Reward points removed.")
        return redirect("spareparts:checkout")
    
    if request.method == "POST" and "payment_method" in request.POST:
        form = PaymentChoiceForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data["payment_method"]
            cart.service_center = form.cleaned_data["service_center"]
            cart.payment_method = method
            cart.status = PartOrder.STATUS_PLACED
            if method == PartOrder.PAYMENT_METHOD_RAZORPAY:
                cart.save(update_fields=["service_center", "payment_method", "status"])
                return redirect("spareparts:razorpay_payment", pk=cart.pk)
            cart.payment_status = PartOrder.PAYMENT_PENDING_CASH
            cart.save(update_fields=["service_center", "payment_method", "payment_status", "status"])
            
            # Recalculate total before awarding points
            cart.recalc_total()

            if cart.points_redeemed > 0:
                reward_account = RewardAccount.objects.filter(user=request.user).first()
                if reward_account:
                    points_used = min(reward_account.points, cart.points_redeemed)
                    reward_account.points -= points_used
                    reward_account.save(update_fields=["points"])
                    if points_used != cart.points_redeemed:
                        cart.points_redeemed = points_used
                        cart.points_discount = (Decimal(points_used) / Decimal("10")).quantize(Decimal("0.01"))
                        cart.save(update_fields=["points_redeemed", "points_discount"])

            # Award reward points based on final total amount
            points_awarded = award_points(request.user, cart.total_amount, "Spare parts purchase")
            if points_awarded > 0:
                messages.success(request, f"Order placed. You earned {points_awarded} reward points!")
            else:
                messages.success(request, "Order placed.")
            return redirect("spareparts:order_detail", pk=cart.pk)
    else:
        form = PaymentChoiceForm(
            initial={
                "service_center": cart.service_center_id,
                "payment_method": cart.payment_method or PaymentChoiceForm.PAYMENT_RAZORPAY,
            }
        )

    reward_account = RewardAccount.objects.filter(user=request.user).first()
    available_points = reward_account.points if reward_account else 0
    coupons = Coupon.objects.filter(active=True)
    return render(request, "spareparts/checkout.html", {"cart": cart, "form": form, "available_coupons": coupons, "available_points": available_points})


@login_required
def razorpay_payment(request, pk):
    order = get_object_or_404(PartOrder, pk=pk, user=request.user)
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Razorpay keys are not configured. Please add test keys to continue.")
        return redirect("spareparts:checkout")

    order.recalc_total()
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_display = Decimal(order.total_amount).quantize(Decimal("0.01"))
    amount_paise = int(amount_display * 100)
    rp_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"partorder_{order.pk}",
        "payment_capture": 1,
    })
    order.razorpay_order_id = rp_order.get("id", "")
    order.save(update_fields=["razorpay_order_id"])

    return render(
        request,
        "spareparts/razorpay_payment.html",
        {
            "order": order,
            "amount_display": amount_display,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": order.razorpay_order_id,
            "amount_paise": amount_paise,
        },
    )


@login_required
def razorpay_verify(request, pk):
    order = get_object_or_404(PartOrder, pk=pk, user=request.user)
    if request.method != "POST":
        return redirect("spareparts:razorpay_payment", pk=pk)
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.error(request, "Razorpay keys are not configured.")
        return redirect("spareparts:checkout")

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
        return redirect("spareparts:razorpay_payment", pk=pk)

    order.payment_method = PartOrder.PAYMENT_METHOD_RAZORPAY
    order.payment_status = PartOrder.PAYMENT_PAID
    order.status = PartOrder.STATUS_PLACED
    order.razorpay_order_id = order_id
    order.razorpay_payment_id = payment_id
    order.save(update_fields=["payment_method", "payment_status", "status", "razorpay_order_id", "razorpay_payment_id"])
    order.recalc_total()

    if order.points_redeemed > 0:
        reward_account = RewardAccount.objects.filter(user=request.user).first()
        if reward_account:
            points_used = min(reward_account.points, order.points_redeemed)
            reward_account.points -= points_used
            reward_account.save(update_fields=["points"])
            if points_used != order.points_redeemed:
                order.points_redeemed = points_used
                order.points_discount = (Decimal(points_used) / Decimal("10")).quantize(Decimal("0.01"))
                order.save(update_fields=["points_redeemed", "points_discount"])

    points_awarded = award_points(request.user, order.total_amount, "Spare parts purchase")
    if points_awarded > 0:
        messages.success(request, f"Payment successful. You earned {points_awarded} reward points!")
    else:
        messages.success(request, "Payment successful.")
    return redirect("spareparts:order_detail", pk=order.pk)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(PartOrder.objects.select_related("service_center"), pk=pk, user=request.user)
    order.recalc_total()
    return render(request, "spareparts/order_detail.html", {"order": order})


@login_required
def my_orders(request):
    orders = (
        PartOrder.objects.select_related("service_center")
        .filter(user=request.user)
        .exclude(status=PartOrder.STATUS_CART)
        .order_by("-created_at")
    )
    return render(request, "spareparts/my_orders.html", {"orders": orders})


def api_parts(request):
    qs = SparePart.objects.all()
    data = []
    for p in qs:
        data.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price) if p.price is not None else None,
            'quantity': p.quantity,
            'image_url': p.image_url,
            'description': p.description,
        })
    return JsonResponse({'parts': data})
