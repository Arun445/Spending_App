from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        # Test creating a new user with an email successfull
        email = 'johndoe@email.com'
        password = 'password123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test the email for a new user is normalized
        email = 'johndoe@EMAIL.com'

        user = User.objects.create_user(email, '123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Test creating user with no email raises error
        with self.assertRaises(ValueError):
            User.objects.create_user(None, '123')

    def test_create_new_super_user(self):
        # Test creating new super user
        user = User.objects.create_superuser(
            'johndoe@EMAIL.com',
            'password123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
