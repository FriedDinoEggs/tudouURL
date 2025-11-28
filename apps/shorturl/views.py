from django.db.models import F
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .models import ShortUrls
from .serializers import ShortUrlsSerializer
from .services import ShortUrlService
from .tasks import store_log


# Create your views here.
class ShortUrlsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ShortUrlsSerializer

    def get_queryset(self):
        queryset = ShortUrls.objects.all()

        return queryset.order_by('-is_active', 'create_at')

    def destroy(self, request, pk=None):
        instance = self.get_object()

        instance.is_deleted = True
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


def redirectShortCode(request, short_code):
    try:
        original_id = ShortUrlService.decode(short_code)

        short_url_instance = get_object_or_404(ShortUrls, pk=original_id, is_active=True)
        short_url_instance.clicks_count = F('clicks_count') + 1
        short_url_instance.save(update_fields=['clicks_count'])

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        log_ip_address = x_forwarded_for if x_forwarded_for else request.META.get('REMOTE_ADDR')
        log_user_agent = request.META.get('HTTP_USER_AGENT', '')
        log_referer = request.META.get('HTTP_REFERER')

        store_log.delay(
            short_url_id=short_url_instance.id,
            ip_address=log_ip_address,
            user_agent=log_user_agent,
            referer=log_referer,
        )

        return redirect(short_url_instance.original_url)

    except ValueError:
        return HttpResponseNotFound('The requested short URL contains invalid characters.')
