# Generated by Django 5.1.3 on 2024-12-07 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0008_product_is_active"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="is_active",
            new_name="in_stock",
        ),
        migrations.RemoveField(
            model_name="product",
            name="is_digital",
        ),
    ]
