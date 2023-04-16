from django.contrib import admin
from .models import Customer
from .models import Product
from .models import Order
#for importing all models
from .models import *
# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Tag)