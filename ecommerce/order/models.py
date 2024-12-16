from django.db import models
from django.conf import settings
from product.models import Product


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PNG", "Pending"
        PREPARING = "PRP", "Preparing"
        RECIEVED = "SHP", "SHIPPED"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.name} is {self.status}"

    def calculate_total_price(self):
        self.total_price = sum(
            item.product.price * item.quantity for item in self.items.all()
        )
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
