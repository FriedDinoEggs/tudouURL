from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import ShortUrlsViewSet

router = DefaultRouter()
router.register(r'shorturls', ShortUrlsViewSet, basename='shorturls')

urlpatterns = router.urls

urlpatterns += [
    # --- API 文件相關 ---
    # 1. 下載 Schema 檔案 (一定要有這個，下面兩個 UI 都是讀這個檔案)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # 2. Swagger UI (推薦用這個)
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    # 3. Redoc UI (選用)
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
