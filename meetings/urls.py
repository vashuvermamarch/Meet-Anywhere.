from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('meet/<str:room_name>/', views.meeting, name='meeting'),
    path('meet/<str:room_name>/waiting/', views.waiting_room, name='waiting_room'),
    path('meet/<str:room_name>/status/', views.check_request_status, name='check_status'),
    path('meet/<str:room_name>/manage/', views.manage_requests, name='manage_requests'),
    path('meet/<str:room_name>/respond/', views.respond_to_request, name='respond_request'),
    path('meet/<str:room_name>/end/', views.end_meeting, name='end_meeting'),
]
