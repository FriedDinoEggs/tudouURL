from django.db.models import F
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import AccessLog, ShortUrls
from .serializers import ShortUrlsSerializer
from .services import ShortUrlGenerater

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


class RedirectView(APIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    @extend_schema(
        summary='Redirect Short URL',
        description='Redirects to the original URL based on the short code.',
        responses={
            302: OpenApiResponse(description='Redirect to target URL'),
            404: OpenApiResponse(description='Not found'),
        },
        request=None,
    )
    def get(self, request, short_code=None):
        try:
            original_id = ShortUrlGenerater.decode(short_code)
            short_url_instance = ShortUrls.objects.get(pk=original_id, is_active=True)
            short_url_instance.clicks_count = F('clicks_count') + 1
            short_url_instance.save(update_fields=['clicks_count'])

            self._set_log(request, instance=short_url_instance)

            return redirect(short_url_instance.original_url)
        except (ValueError, ShortUrls.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def _set_log(self, request, instance):
        log_ip_address = request.META.get('REMOTE_ADDR')
        log_user_agent = request.META.get('HTTP_USER_AGENT', '')
        log_referer = request.META.get('HTTP_REFERER')

        access_log_instance = AccessLog.objects.create(
            short_url_id=instance,
            ip_address=log_ip_address,
            user_agent=log_user_agent,
            referer=log_referer,
        )
