from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Category, Brand, Product, Comment
from PIL import Image
import tempfile


PRODUCTS_URL = reverse("product-list")


def detail_url(product_id):
    return reverse("product-detail", args=[product_id])


def create_product(**params):
    category = Category.objects.create(name="Category Name")
    brand = Brand.objects.create(name="Brand Name")

    defaults = {
        "name": "Product Name",
        "description": "Product Description",
        "in_stock": True,
        "price": 100,
        "category": category,
        "brand": brand,
    }

    defaults.update(**params)

    return Product.objects.create(**defaults)


def create_temp_image(width=10, height=10):
    image_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img = Image.new("RGB", (width, height))
    img.save(image_file, format="JPEG")
    image_file.seek(0)
    return image_file


class NonAdminUserTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com", name="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.product = create_product()

    def test_list_product_success(self):
        res = self.client.get(PRODUCTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_product_success(self):
        url = detail_url(self.product.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], self.product.name)

    def test_create_product_error(self):
        payload = {"name": "New Product"}
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_error(self):
        payload = {"name": "Updated Product"}
        url = detail_url(self.product.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_error(self):
        url = detail_url(self.product.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTest(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="user@admin.com", name="Admin User", password="passadminuser"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin_user)
        self.brand = Brand.objects.create(name="Brand Test Name")
        self.product = create_product()
        self.comment1 = Comment.objects.create(
            user=self.admin_user, product=self.product, rating=4
        )
        self.comment2 = Comment.objects.create(
            user=self.admin_user, product=self.product, rating=3
        )

    def test_create_product_success(self):
        payload = {
            "name": "Product Name",
            "brand": self.brand.id,
        }

        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], payload["name"])

    def test_update_product_success(self):
        payload = {"name": "Updated Product"}
        url = detail_url(self.product.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, payload["name"])

    def test_delete_product_success(self):
        url = detail_url(self.product.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_product_comments(self):
        url = detail_url(self.product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("comments", res.data)

        self.assertEqual(len(res.data["comments"]), 2)
        self.assertEqual(res.data["comments"][0]["id"], self.comment1.id)
        self.assertEqual(res.data["comments"][0]["rating"], self.comment1.rating)
        self.assertEqual(res.data["comments"][1]["id"], self.comment2.id)
        self.assertEqual(res.data["comments"][1]["rating"], self.comment2.rating)

    def test_avarage_and_number_rating_field(self):
        url = detail_url(self.product.id)
        res = self.client.get(url)

        avarage_rating = (self.comment1.rating + self.comment2.rating) / 2

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data["average_rating"], avarage_rating)
        self.assertEqual(res.data["number_of_ratings"], 2)

    def test_create_product_with_image_success(self):
        image_file = create_temp_image()
        payload = {
            "name": "Product with Image",
            "brand": self.brand.id,
            "image": image_file,
        }

        res = self.client.post(PRODUCTS_URL, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("image", res.data)
        self.assertTrue(res.data["image"].startswith("http://testserver/media/images/"))

    def test_update_product_image_success(self):
        old_image_file = create_temp_image()
        self.product.image.save("old_image.jpg", old_image_file)

        new_image_file = create_temp_image()
        payload = {"image": new_image_file}
        url = detail_url(self.product.id)

        res = self.client.patch(url, payload, format="multipart")

        self.product.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        temp_filename = new_image_file.name.split("/")[-1]
        product_filename = self.product.image.name.split("/")[-1]

        self.assertEqual(temp_filename, product_filename)
        self.assertTrue(self.product.image.name.startswith("images/"))
        self.assertTrue(res.data["image"].startswith("http://testserver/media/images/"))
