from django.db import models

# Create your models here.
class WebexUserSession(models.Model):
    webhook_id = models.CharField(max_length=150)
    channel_name = models.CharField(max_length=150)