# Generated by Django 5.1.3 on 2024-12-08 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[("PNG", "Pending"), ("PRP", "Preparing"), ("SHP", "SHIPPED")],
                default="PNG",
                max_length=3,
            ),
        ),
    ]
