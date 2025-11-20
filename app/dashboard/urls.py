from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_section, name='dashboard'),
    path('<int:page_id>/', views.dashboard_section, name='dashboard_section'),
]