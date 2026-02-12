from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list, name='list'),
    path('mine/', views.my_vehicle_list, name='mine'),
    path('add/', views.vehicle_create, name='create'),
    path('<int:pk>/', views.vehicle_detail, name='detail'),
]
