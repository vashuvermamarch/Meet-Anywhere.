from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('meet/<str:room_name>/', views.meeting, name='meeting'),
    path('meet/<str:room_name>/end/', views.end_meeting, name='end_meeting'),
    
    # Gatekeeper API
    path('api/meet/<str:room_name>/request/', views.api_request_join, name='api_request_join'),
    path('api/request/<int:request_id>/status/', views.api_check_status, name='api_check_status'),
    path('api/meet/<str:room_name>/requests/', views.api_get_requests, name='api_get_requests'),
    path('api/request/<int:request_id>/approve/', views.api_approve_request, name='api_approve_request'),
]
