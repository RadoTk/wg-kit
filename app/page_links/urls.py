# page_links/urls.py
from django.urls import path
from .views import redirect_to_link
from .views import store_product_redirect


app_name = 'page_links'
urlpatterns = [
    path('go/<str:source_model>/<int:source_id>/', redirect_to_link, name='redirect-to-link'),
    path('goto/product/<int:product_id>/', store_product_redirect, name='store-product-redirect'),
]
