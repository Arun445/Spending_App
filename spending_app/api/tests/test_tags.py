from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Tag
from api.serializers import TagSerializer

User = get_user_model()
TAG_URL = reverse('api:tag-list')


class PublicTagApiTests(TestCase):
    # Test the publicly accesable Tags api
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    # Tests that are privately acessable by an authorized user

    def setUp(self):
        self.user = User.objects.create(
            email='test@email.com', name='test', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_all_tags(self):
        # Test to list all users tags
        Tag.objects.create(name='testtag1', user=self.user)
        Tag.objects.create(name='testtag2', user=self.user)
        response = self.client.get(TAG_URL)
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        # Test to list only the authenticated users tags
        user2 = User.objects.create(
            email='test2@email.com', name='test2', password='testpassword')
        Tag.objects.create(name='testtag1', user=user2)
        tag = Tag.objects.create(name='testtag2', user=self.user)
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_tags_crate_successful(self):
        # Test to create a tag succesfuly
        payload = {'name': 'testtag'}
        response = self.client.post(TAG_URL, payload)
        exist = Tag.objects.filter(user=self.user, name=payload['name'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exist)

    def test_tags_create_invalid(self):
        # Test to create a tag with invalid input
        payload = {'name': ''}
        response = self.client.post(TAG_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
