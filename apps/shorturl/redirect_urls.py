from django.urls import path

# from .views import RedirectView
from .views import redirectShortCode

urlpatterns = [
    path('<str:short_code>/', redirectShortCode, name='redirect')
    # path('<str:short_code>/', RedirectView.as_view(), name='redirect')
]
