from django.db import models

# Create your models here.
class CreatorHandles(models.Model):
    creators_handle = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.creators_handle}"


class Character(models.Model):
    name = models.CharField(max_length=255)
    total_chats = models.IntegerField()
    total_messages = models.IntegerField()
    likes = models.IntegerField()
    dislikes = models.IntegerField()
    creator = models.CharField(max_length=255)
    published_date = models.DateField()
    last_updated = models.CharField(max_length=255)
    avg_messages_per_day = models.FloatField()
    avg_chats_per_day = models.FloatField()
    avg_likes_per_day = models.FloatField()
