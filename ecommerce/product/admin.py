from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Brand, Product

# Register your models here.
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Brand)
admin.site.register(Product)
