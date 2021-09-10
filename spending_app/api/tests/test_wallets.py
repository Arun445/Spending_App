from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Wallet
from api import serializers

User = get_user_model()
WALLET_URL = reverse('api:wallet-list')


class PublicTests(TestCase):
    # Tests public access
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        response = self.client.get(WALLET_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTests(TestCase):
    # Test authenticated user access
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@email.com', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_wallets(self):
        # Test to retrieve all the authenticate users wallets
        Wallet.objects.create(
            user=self.user, name='testwallet', currency='EUR', balance=100)
        Wallet.objects.create(
            user=self.user, name='testwallet2', currency='EUR', balance=200)
        response = self.client.get(WALLET_URL)
        wallets = Wallet.objects.all().order_by('-balance')
        serializer = serializers.WalletSerializer(wallets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.data[0]['name'], wallets[0].name)

    def test_wallets_limited_to_user(self):
        # Test to retrieve only the wallets that are created by that user
        user2 = User.objects.create_user(
            email='test2@email.com', password='password123')
        wallet = Wallet.objects.create(
            user=self.user, name='testwallet', currency='EUR', balance=100)
        Wallet.objects.create(
            user=user2, name='testwallet2', currency='EUR', balance=20)

        response = self.client.get(WALLET_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wallet.name)

    def test_create_wallet_successful(self):
        # Test create wallet with a post request success
        payload = {
            'user': self.user.id,
            "name": "testwallet",
            "currency": "EUR",
            "balance": 100
        }
        response = self.client.post(WALLET_URL, payload)
        exist = Wallet.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exist)

    def test_create_wallet_no_input(self):
        # Test to create a new wallet with invalid input
        payload = {
            'user': self.user.id,
            'name': '',
            'currency': 'EUR',

        }
        response = self.client.post(WALLET_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
