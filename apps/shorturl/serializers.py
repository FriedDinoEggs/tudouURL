from django.urls import reverse
from rest_framework import serializers

from .models import AccessLog, ShortUrls
from .services import ShortUrlService


class ShortUrlsSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    def get_short_url(self, obj) -> None | str:
        if not obj.id:
            return None

        request = self.context.get('request')
        if not request:
            return None

        short_code = ShortUrlService.encode(obj.id)
        relative_url = reverse('redirect', kwargs={'short_code': short_code})
        return request.build_absolute_uri(relative_url)

    class Meta:
        model = ShortUrls
        # fields = '__all__'
        fields = [
            'id',
            'original_url',
            'short_url',
            'create_at',
            'expires_at',
            'is_active',
            'clicks_count',
        ]
        read_only_fields = ['clicks_count', 'short_url']

    def create(self: ShortUrlsSerializer, validated_data):
        validated_data['clicks_count'] = 0
        return ShortUrls.objects.create(**validated_data)

    def update(self: ShortUrlsSerializer, instance: ShortUrls, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.original_url = validated_data.get('original_url', instance.original_url)
        instance.save()

        return instance


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = ['id', 'short_url_id', 'accessed_at', 'ip_address', 'user_agent', 'referer']
        read_only_fields = [
            'id',
            'short_url_id',
            'accessed_at',
            'ip_address',
            'user_agent',
            'referer',
        ]
