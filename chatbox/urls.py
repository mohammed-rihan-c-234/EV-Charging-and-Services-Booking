from django.urls import path
from . import views

app_name = 'chatbox'

urlpatterns = [
    path('', views.chats, name='list'),
    path('new/', views.chat_create, name='create'),
    path('<int:pk>/', views.chat_detail, name='detail'),
]
