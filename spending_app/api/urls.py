from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet

router = DefaultRouter()
router.register('transactions', TransactionViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls))
]
