from django.contrib import admin

from .models import ShortUrls

# Register your models here.


@admin.register(ShortUrls)
class ShortUrlsAdmin(admin.ModelAdmin):
    list_display = ['original_url', 'create_at', 'expires_at', 'is_active', 'clicks_count']
