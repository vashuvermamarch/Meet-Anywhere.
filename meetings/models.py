from django.db import models
from django.contrib.auth.models import User
import uuid

class Meeting(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    room_name = models.CharField(max_length=255, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_meetings')
    authorized_participants = models.ManyToManyField(User, related_name='joined_meetings', blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.room_name:
            self.room_name = self.room_name.lower().strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room_name} (Host: {self.host.username})"

class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('meeting', 'user')

    def __str__(self):
        return f"{self.user.username} -> {self.meeting.room_name} ({self.status})"
