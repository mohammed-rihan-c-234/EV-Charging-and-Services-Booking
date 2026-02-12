from django.urls import path
from . import views

app_name = 'sos'

urlpatterns = [
    path('', views.sos_list, name='list'),
    path('new/', views.sos_submit, name='submit'),
    # API endpoint for IoT or external services to POST alerts
    path('api/receive/', views.api_receive_alert, name='api_receive'),
]
