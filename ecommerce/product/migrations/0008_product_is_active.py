# Generated by Django 5.1.3 on 2024-12-07 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0007_alter_comment_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
