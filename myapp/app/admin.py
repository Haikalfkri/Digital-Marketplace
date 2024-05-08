from django.contrib import admin
from app.models import Product, OrderDetail

# Register your models here.
admin.site.register(Product)
admin.site.register(OrderDetail)