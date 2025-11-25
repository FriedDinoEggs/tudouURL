from datetime import timedelta

from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, expires_at__gt=timezone.now())


class ShortUrls(models.Model):
    # short_code = models.fields.CharField(max_length=64, unique=True, db_index=True)
    original_url = models.fields.URLField(max_length=2048)
    create_at = models.fields.DateTimeField(auto_now_add=True)
    expires_at = models.fields.DateTimeField(default=timezone.now() + timedelta(days=10))
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    clicks_count = models.fields.IntegerField(default=0)

    objects = ActiveManager()

    def __str__(self):
        return self.original_url


class AccessLog(models.Model):
    short_url_id = models.ForeignKey(ShortUrls, on_delete=models.CASCADE, related_name='logs')
    accessed_at = models.fields.DateTimeField(auto_now=True)
    ip_address = models.fields.GenericIPAddressField(null=True, blank=True)
    user_agent = models.fields.CharField(blank=True, max_length=1024)
    referer = models.fields.URLField(null=True, blank=True, max_length=2048)
