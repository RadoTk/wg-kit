from django.urls import path
from . import views

urlpatterns = [
    path('', views.confession_list, name='confession_list'),
    path('create/', views.confession_create, name='confession_create'),
    path('anonymous-create/', views.confession_anonymous_create, name='confession_anonymous_create'),
    path('<int:pk>/', views.confession_detail, name='confession_detail'),
    path('category/<int:category_id>/', views.confession_category_list, name='confession_category_list'),
]