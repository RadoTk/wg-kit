from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path('add/<int:product_id>/', views.cart_add, name='add'),
    path('', views.show_cart_detail, name='cart_detail'),
    path('remove/<int:product_id>/', views.cart_remove, name='remove'),
    path('update/<int:product_id>/', views.cart_update, name='update'),
]
