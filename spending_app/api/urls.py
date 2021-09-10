from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, WalletViewSet

router = DefaultRouter()
router.register('transactions', TransactionViewSet)
router.register('wallets', WalletViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls))
]
