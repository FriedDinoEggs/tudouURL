from django.shortcuts import redirect
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ShortUrls
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
    def get(self, request, short_code=None):
        try:
            original_id = ShortUrlGenerater.decode(short_code)
            short_url_instance = ShortUrls.objects.get(pk=original_id, is_active=True)
            short_url_instance.clicks_count += 1
            short_url_instance.save(update_fields=['clicks_count'])

            return redirect(short_url_instance.original_url)
        except (ValueError, ShortUrls.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
