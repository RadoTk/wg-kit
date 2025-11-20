from django.urls import path
from .views import user_dashboard

app_name = "dashboard"

urlpatterns = [
    path("", user_dashboard, name="user_dashboard"),
]
