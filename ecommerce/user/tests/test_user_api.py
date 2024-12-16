from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class RegisterApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("user:register")

    def test_register_user_success(self):
        payload = {
            "email": "example@user.com",
            "name": "Example User",
            "password": "examplepass123",
            "password2": "examplepass123",
        }

        res = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            get_user_model().objects.filter(email=payload["email"]).exists()
        )

    def test_register_user_without_email_error(self):
        payload = {
            "name": "Example User",
            "password": "examplepass123",
            "password2": "examplepass123",
        }

        res = self.client.post(self.register_url, payload, format="json")
        self.assertIn("email", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_existing_email_error(self):
        newuser = get_user_model().objects.create_user(
            email="test@user.com",
            name="Test User",
            password="userpass123",
        )

        payload = {
            "email": newuser.email,
            "name": "Example User",
            "password": "examplepass123",
            "password2": "examplepass123",
        }

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_without_password_error(self):
        payload = {
            "email": "example@user.com",
            "name": "Example User",
        }

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_short_password_error(self):
        payload = {
            "email": "example@user.com",
            "name": "Example User",
            "password": "pw",
            "password2": "pw",
        }

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_mismatched_passwords_error(self):
        payload = {
            "email": "example@user.com",
            "name": "Example User",
            "password": "examplepass123",
            "password2": "differentpass123",
        }

        res = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test9@user.com",
            name="Test User",
            password="userpass123",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.login_url = reverse("user:login")

    def test_user_login_success(self):
        payload = {
            "email": self.user.email,
            "password": "userpass123",
        }
        res = self.client.post(self.login_url, payload, format="json")

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_with_bad_credentials(self):
        payload = {
            "email": self.user.email,
            "password": "badpass",
        }

        res = self.client.post(self.login_url, payload, format="json")

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class ManageUserApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test9@user.com",
            name="Test User",
            password="userpass123",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.me_url = reverse("user:me")

    def test_retrieve_profile_success(self):
        res = self.client.get(self.me_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["name"], self.user.name)

    def test_update_user_profile_success(self):
        payload = {
            "name": "Updated name",
            "password": "newpassword123",
            "password2": "newpassword123",
        }

        res = self.client.patch(self.me_url, payload, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_update_mismatch_error(self):
        payload = {
            "name": "Updated Name",
            "password": "newpassword123",
            "password2": "mismatchedpassword",
        }

        res = self.client.patch(self.me_url, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("userpass123"))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthenticated(self):
        new_client = APIClient()
        res = new_client.get(self.me_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
