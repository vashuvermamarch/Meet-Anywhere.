from django.db import models

class MeetingRoom(models.Model):
    room_name = models.CharField(max_length=255, unique=True)
    is_host_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_name} (Active: {self.is_host_active})"

class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='join_requests')
    guest_name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guest_name} -> {self.room.room_name} ({self.status})"
