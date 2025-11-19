from django.urls import path
from .views import AnimalCreateView, animal_detail

app_name = 'animals'

urlpatterns = [
    path('add/', AnimalCreateView.as_view(), name='animal_add'),
    path('<int:pk>/', animal_detail, name='animal_detail'),
]
