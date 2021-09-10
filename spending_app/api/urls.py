from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, WalletViewSet, TagViewSet

router = DefaultRouter()
router.register('transactions', TransactionViewSet)
router.register('wallets', WalletViewSet)
router.register('tags', TagViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls))
]
