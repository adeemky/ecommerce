# Generated by Django 5.1.3 on 2024-11-29 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=99.0, max_digits=10),
        ),
    ]
