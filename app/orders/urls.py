from django.urls import path
from . import views
from .views import order_create
from .views import stripe_webhook

app_name = 'orders'

urlpatterns = [
    path('create/', order_create, name="order_create"),
    path('thanks/', views.order_success_view, name='order_thanks'),
    path("refresh-badge/", views.get_new_orders_count, name="refresh_order_badge"),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
