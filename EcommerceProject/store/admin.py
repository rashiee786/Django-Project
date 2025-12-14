from django.contrib import admin
from .models import Product, Order, OrderProduct, UserProfile

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)
    list_filter = ('price',)

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_date')
    list_filter = ('status', 'order_date')
    inlines = [OrderProductInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


# import os 
# import sys 
# # --- Add your project path --- 
# project_path = 
# '/home/LekshmiWeb/DJANGO-PROJECT/Student_Management' 
# if project_path not in sys.path: 
# sys.path.append(project_path) 
# # --- Activate Virtualenv (Python 3.13) --- 
# activate_this = 
# '/home/LekshmiWeb/.virtualenvs/djangoenv/bin/activate_this.p
#  y' 
# with open(activate_this) as f: 
# exec(f.read(), dict(__file__=activate_this)) 
# # --- Django settings --- 
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 
# 'Student_Management.settings') 
# from django.core.wsgi import get_wsgi_application 
# application = get_wsgi_application()


