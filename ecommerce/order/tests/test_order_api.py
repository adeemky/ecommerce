from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import mail
from product.models import Product, Brand
from ..models import Order, OrderItem


def create_product(**params):
    brand, _ = Brand.objects.get_or_create(name="Brand Name")
    defaults = {
        "name": "Test Product Name",
        "brand": brand,
        "price": 100,
    }
    defaults.update(params)
    return Product.objects.create(**defaults)


def create_order(user, **params):
    defaults = {"user": user, "total_price": 0}
    defaults.update(params)
    return Order.objects.create(**defaults)


def create_order_item(order, product, quantity=1):
    return OrderItem.objects.create(order=order, product=product, quantity=quantity)


def create_order_and_items(user):
    product = create_product()
    order = create_order(user=user, total_price=product.price * 3)
    create_order_item(order, product, quantity=3)
    return order


def detail_url(order_id):
    return reverse("order-detail", args=[order_id])


class PublicOrdersAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.orders_url = reverse("order-list")

    def test_list_orders_auth_required(self):
        res = self.client.get(self.orders_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_auth_required(self):
        product = create_product()
        payload = {"items": [{"product": product.id, "quantity": 2}]}

        res = self.client.post(self.orders_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrdersAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test9@user.com",
            name="Test User",
            password="userpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.orders_url = reverse("order-list")

    def test_list_orders_success(self):
        create_order_and_items(user=self.user)
        create_order_and_items(user=self.user)

        res = self.client.get(self.orders_url)

        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_orders_limited_to_user(self):
        other_user = get_user_model().objects.create_user(
            name="Other User", email="other@user.com", password="examplepass123"
        )
        create_order_and_items(user=other_user)
        create_order_and_items(user=self.user)

        res = self.client.get(self.orders_url)
        order = res.data[0]

        self.assertEqual(len(res.data), 1)
        self.assertEqual(order["user"], self.user.name)

    def test_create_order_success(self):
        product1 = create_product()
        payload = {
            "items": [
                {"product": product1.id, "quantity": 2},
                {"product": product1.id, "quantity": 1},
            ],
        }

        res = self.client.post(self.orders_url, payload, format="json")

        self.assertEqual(len(res.data["items"]), 2)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"], self.user.name)

        total_price = sum(
            item["quantity"] * product1.price for item in payload["items"]
        )
        self.assertEqual(res.data["total_price"], total_price)


class PrivateOrderDetailAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            name="Test User",
            password="userpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_order_success(self):
        order = create_order_and_items(user=self.user)

        url = detail_url(order.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"], self.user.name)

    def test_update_order_success(self):
        order = create_order_and_items(user=self.user)
        product1 = create_product(name="Product1 Name", price=300)
        product2 = create_product(name="Product2 Name", price=200)

        payload = {
            "items": [
                {"product": product1.id, "quantity": 2},
                {"product": product2.id, "quantity": 3},
            ]
        }

        url = detail_url(order.id)
        res = self.client.put(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        order.refresh_from_db()

        self.assertEqual(order.items.count(), 2)
        item1 = order.items.get(product=product1)
        self.assertEqual(item1.quantity, 2)
        item2 = order.items.get(product=product2)
        self.assertEqual(item2.quantity, 3)

    def test_status_update_error(self):
        order = create_order_and_items(user=self.user)

        payload = {"status": "SHP"}

        url = detail_url(order.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_error(self):
        other_user = get_user_model().objects.create_user(
            name="Other User", email="other@user.com", password="examplepass123"
        )

        order = create_order_and_items(user=self.user)

        payload = {"user": other_user.id}

        url = detail_url(order.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order(self):
        order = create_order_and_items(user=self.user)

        url = detail_url(order.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        order_exists = Order.objects.filter(id=order.id).exists()
        self.assertFalse(order_exists)

    def test_update_other_users_order_error(self):
        other_user = get_user_model().objects.create_user(
            name="Other User", email="other@user.com", password="examplepass123"
        )
        order = create_order_and_items(user=other_user)
        product = create_product(name="Unauthorized Update", price=500)

        payload = {"items": [{"product": product.id, "quantity": 1}]}

        url = detail_url(order.id)
        res = self.client.put(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_other_users_order_error(self):
        other_user = get_user_model().objects.create_user(
            name="Other User", email="other@user.com", password="examplepass123"
        )
        order = create_order_and_items(user=other_user)

        url = detail_url(order.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_email_sent_on_status_change_to_shipped(self):
        order = create_order_and_items(user=self.user)

        order.status = "SHP"
        order.save()

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, f"Order #{order.id} has been shipped")
        self.assertIn(f"Your order #{order.id} has been shipped.", email.body)
        self.assertEqual(email.to, [self.user.email])
