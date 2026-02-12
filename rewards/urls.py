from django.urls import path
from . import views

app_name = 'rewards'

urlpatterns = [
    path('', views.rewards_list, name='list'),
    path('api/me/', views.api_my_rewards, name='api_my_rewards'),
]
