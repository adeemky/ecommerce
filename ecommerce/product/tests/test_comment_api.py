from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Brand, Product, Comment

COMMENTS_URL = reverse("comment-list")


def detail_url(comment_id):
    return reverse("comment-detail", args=[comment_id])


def create_user(**params):
    defaults = {
        "name": "New Test User",
        "email": "newtest@user.com",
        "password": "passnewtestuser",
    }
    defaults.update(**params)
    return get_user_model().objects.create_user(**defaults)


def create_product(**params):
    brand = Brand.objects.create(name="Brand Name")

    defaults = {
        "name": "Product Name",
        "brand": brand,
    }

    defaults.update(**params)

    return Product.objects.create(**defaults)


def create_comment(user, product, **params):
    defaults = {
        "user": user,
        "product": product,
        "rating": 4,
        "comment_text": "Test Comment",
    }

    defaults.update(**params)

    return Comment.objects.create(**defaults)


class UnAuthorizedUserTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = create_product()

    def test_list_comments_success(self):
        res = self.client.get(COMMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_comment_success(self):
        user = create_user()
        comment = create_comment(user=user, product=self.product)

        url = detail_url(comment.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], comment.user.name)
        self.assertEqual(res.data["product"], comment.product.id)
        self.assertEqual(res.data["rating"], comment.rating)
        self.assertEqual(res.data["comment_text"], comment.comment_text)

    def test_create_comment_error(self):
        payload = {
            "product": self.product.id,
            "rating": 4,
            "comment_text": "Test Comment",
        }

        res = self.client.post(COMMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_error(self):
        user = create_user()
        comment = create_comment(user=user, product=self.product)

        payload = {"rating": 2}

        url = detail_url(comment.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_error(self):
        user = create_user()
        comment = create_comment(user=user, product=self.product)

        url = detail_url(comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserTest(APITestCase):
    def setUp(self):
        self.user = create_user()
        self.another_user = create_user(
            email="another@user.com", name="Another User", password="passanotheruser"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.product = create_product()
        self.comment = create_comment(user=self.user, product=self.product)

    def test_create_comment_success(self):
        new_product = create_product()
        payload = {
            "product": new_product.id,
            "rating": 4,
            "comment_text": "Test Comment",
        }

        res = self.client.post(COMMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"], self.comment.user.name)
        self.assertEqual(res.data["product"], payload["product"])
        self.assertEqual(res.data["rating"], payload["rating"])
        self.assertEqual(res.data["comment_text"], payload["comment_text"])

    def test_update_comment_success(self):
        payload = {"rating": 2, "comment_text": "Updated Comment"}

        url = detail_url(self.comment.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.rating, payload["rating"])
        self.assertEqual(self.comment.comment_text, payload["comment_text"])

    def test_delete_comment_success(self):
        url = detail_url(self.comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_duplicate_product_comment_error(self):
        payload = {
            "product": self.product.id,
            "rating": 5,
        }
        res = self.client.post(COMMENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_other_users_comment_error(self):
        another_comment = create_comment(user=self.another_user, product=self.product)

        payload = {"rating": 3}
        url = detail_url(another_comment.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_users_comment_error(self):
        another_comment = create_comment(user=self.another_user, product=self.product)

        url = detail_url(another_comment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_field_error(self):
        payload = {"user": self.another_user.id}

        url = detail_url(self.comment.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_rating_value(self):
        invalid_ratings = [6, 0, -1]
        for rating in invalid_ratings:
            payload = {
                "product": self.product.id,
                "rating": rating,
            }
            res = self.client.post(COMMENTS_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
