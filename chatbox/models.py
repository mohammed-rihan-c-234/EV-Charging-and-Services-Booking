from django.db import models
from django.conf import settings
from service_center.models import ServiceCenter

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    service_center = models.ForeignKey(
        ServiceCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_sessions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"ChatSession {self.pk} - {username}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = 'User' if self.is_user else 'Agent'
        return f"{who}: {self.text[:30]}"
