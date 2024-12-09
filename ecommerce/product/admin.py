from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Brand, Product, Comment

# Register your models here.
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Comment)
