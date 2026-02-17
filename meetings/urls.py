from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('meet/<str:room_name>/', views.meeting, name='meeting'),
]
