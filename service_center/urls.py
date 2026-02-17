from django.urls import path
from . import views

app_name = 'service_center'

urlpatterns = [
    path('', views.center_list, name='list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('dashboard/booking/<int:pk>/decide/', views.booking_decide, name='booking_decide'),
    path('dashboard/order/<int:pk>/decide/', views.order_decide, name='order_decide'),
    path('api/centers/', views.api_centers, name='api_centers'),
]
