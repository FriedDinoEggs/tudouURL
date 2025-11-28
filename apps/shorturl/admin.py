from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import AccessLog, ShortUrls
from .serializers import ShortUrlService


# Register your models here.
class AccessLogInline(admin.TabularInline):
    model = AccessLog

    # 預設不新增額外的空白表單
    extra = 0

    # 不能刪除
    can_delete = False

    max_num = 0

    # fields = ['short_url_id', 'accessed_at', 'ip_address', 'user_agent', 'referer']
    readonly_fields = ['short_url_id', 'accessed_at', 'ip_address', 'user_agent', 'referer']


@admin.register(ShortUrls)
class ShortUrlsAdmin(admin.ModelAdmin):
    list_display = [
        'display_original_url',
        'display_short_url',
        'create_at',
        'expires_at',
        'is_active',
        'clicks_count',
    ]

    @admin.display(description='original URL~~~')
    def display_original_url(self, obj):
        return format_html(
            """
            <div style="
                width: 200px; 
                max-width: 500px;
                white-space: nowrap; 
                overflow: hidden; 
                text-overflow: ellipsis; 
                resize: horizontal; 
                padding-bottom: 2px;
            " title="{}">{}</div>
            """,
            obj.original_url,  # title 屬性讓滑鼠移上去會顯示完整網址
            obj.original_url,  # 內容
        )

    @admin.display(description='short URL!!!')
    def display_short_url(self, obj):
        return f'{settings.SITE_URL}/{ShortUrlService.encode(obj.id)}'

    inlines = [
        AccessLogInline,
    ]

    list_filter = ['is_deleted', 'is_active']
    list_per_page = 25
    search_fields = ('original_url',)
    ordering = (
        'create_at',
        '-clicks_count',
    )

    fieldsets = [
        (
            None,
            {'fields': ['original_url', 'expires_at', 'is_active']},
        ),
    ]


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['short_url_id', 'accessed_at', 'ip_address', 'user_agent', 'referer']
    ordering = ('id',)
