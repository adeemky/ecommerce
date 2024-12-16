from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Brand

BRANDS_URL = reverse("brand-list")


def detail_url(brand_id):
    return reverse("brand-detail", args=[brand_id])


class NonAdminUserTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com", name="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.brand = Brand.objects.create(name="Test Brand")

    def test_list_brand_success(self):
        res = self.client.get(BRANDS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_brand_success(self):
        url = detail_url(self.brand.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], self.brand.name)

    def test_create_brand_error(self):
        payload = {"name": "New Brand"}
        res = self.client.post(BRANDS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_brand_error(self):
        url = detail_url(self.brand.id)
        payload = {"name": "Updated Brand"}
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_brand_error(self):
        url = detail_url(self.brand.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="user@admin.com", name="Admin User", password="passadminuser"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin_user)
        self.brand = Brand.objects.create(name="Test Brand")

    def test_create_brand_success(self):
        payload = {"name": "New Brand"}
        res = self.client.post(BRANDS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], payload["name"])

    def test_update_brand_success(self):
        url = detail_url(self.brand.id)
        payload = {"name": "Updated Brand"}
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.brand.refresh_from_db()
        self.assertEqual(self.brand.name, payload["name"])

    def test_delete_brand_success(self):
        url = detail_url(self.brand.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Brand.objects.filter(id=self.brand.id).exists())
