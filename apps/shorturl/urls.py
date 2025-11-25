from rest_framework.routers import DefaultRouter

from .views import ShortUrlsViewSet

router = DefaultRouter()
router.register(r'shorturls', ShortUrlsViewSet, basename='shorturls')

urlpatterns = router.urls
