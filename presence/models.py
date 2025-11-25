from django.db import models
from django.conf import settings

class UserActivity(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.last_seen.strftime('%d/%m/%Y %H:%M:%S')}"