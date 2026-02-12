from django.urls import path
from . import views

app_name = 'spareparts'

urlpatterns = [
    path('', views.parts_list, name='list'),
    path('<int:pk>/', views.part_detail, name='detail'),
    path('<int:pk>/add-to-cart/', views.cart_add, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.cart_checkout, name='checkout'),
    path('pay/razorpay/<int:pk>/', views.razorpay_payment, name='razorpay_payment'),
    path('pay/razorpay/<int:pk>/verify/', views.razorpay_verify, name='razorpay_verify'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('api/parts/', views.api_parts, name='api_parts'),
]
