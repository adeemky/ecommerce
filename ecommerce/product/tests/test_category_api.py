from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Category

CATEGORIES_URL = reverse("category-list")


def detail_url(category_id):
    return reverse("category-detail", args=[category_id])


class NonAdminUserTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com", name="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.category = Category.objects.create(name="Test Category")

    def test_list_categories_success(self):
        res = self.client.get(CATEGORIES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_category_success(self):
        url = detail_url(self.category.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], self.category.name)

    def test_create_category_error(self):
        payload = {"name": "New Category"}
        res = self.client.post(CATEGORIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category_error(self):
        url = detail_url(self.category.id)
        payload = {"name": "Updated Category"}
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_error(self):
        url = detail_url(self.category.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="user@admin.com", name="Admin User", password="passadminuser"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin_user)
        self.parent_category = Category.objects.create(name="Parent Category")
        self.child_category = Category.objects.create(
            name="Child Category", parent=self.parent_category
        )

    def test_create_category_success(self):
        payload = {"name": "New Admin Category"}
        res = self.client.post(CATEGORIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], payload["name"])

    def test_update_category_success(self):
        url = detail_url(self.parent_category.id)
        payload = {"name": "Updated Parent Category"}
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.parent_category.refresh_from_db()
        self.assertEqual(self.parent_category.name, payload["name"])

    def test_delete_category_success(self):
        url = detail_url(self.child_category.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.child_category.id).exists())

    def test_parent_child_relationship_success(self):
        url = detail_url(self.child_category.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["parent"], self.parent_category.id)
