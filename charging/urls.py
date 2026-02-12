from django.urls import path
from . import views

app_name = 'charging'

urlpatterns = [
    path('', views.station_list, name='list'),
    path('api/stations/', views.api_stations, name='api_stations'),
    path('<int:station_id>/book/', views.book_charging, name='book'),
    path('booking/<int:booking_id>/confirm/', views.booking_confirmation, name='booking_confirmation'),
    path('bookings/mine/', views.my_charging_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/pay/', views.razorpay_payment, name='razorpay_payment'),
    path('booking/<int:booking_id>/verify/', views.razorpay_verify, name='razorpay_verify'),
]
