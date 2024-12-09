from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.core.mail import send_mail
from .models import Order

@receiver(post_save, sender=Order)
def notify_user_on_status_change(sender, instance, **kwargs):
    if instance.status == 'SHP':
        order_link = f"http://127.0.0.1:8000{reverse('order-detail', args=[instance.id])}"
        subject = f"Order #{instance.id} has been shipped"
        message = f"Your order #{instance.id} has been shipped. You can view the details here: {order_link}"

        send_mail(
            subject,
            message,
            'ecommerce@email.com',
            [instance.user.email],
        )