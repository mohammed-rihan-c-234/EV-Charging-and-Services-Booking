from django.urls import path

from . import views


app_name = "bookings"


urlpatterns = [
    path("new/", views.booking_create, name="booking_create"),
    path("mine/", views.my_bookings, name="my_bookings"),
    path("<int:pk>/", views.booking_detail, name="detail"),
    path("<int:pk>/checkout/", views.booking_checkout, name="checkout"),
    path("<int:pk>/pay/razorpay/", views.razorpay_payment, name="razorpay_payment"),
    path("<int:pk>/pay/razorpay/verify/", views.razorpay_verify, name="razorpay_verify"),
]
