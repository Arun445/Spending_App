from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            email='johndoe@email.com',
            password='password123'
        )
        self.client.force_login(self.admin_user)
        self.user = User.objects.create_user(
            email='tommoe@email.com',
            password='password123',
            name='tom moe'

        )

    def test_users_listed(self):
        # Test that users are listed on user page
        url = reverse('admin:api_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        # Test that the user edit page works
        url = reverse('admin:api_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        # Test that the create user page works
        url = reverse('admin:api_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
