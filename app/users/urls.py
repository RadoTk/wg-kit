from django.urls import path
from .views import UserLoginView, profile_edit, user_logout, signup
from django.contrib.auth.views import LogoutView

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("logout/", user_logout, name="logout"),
    path("signup/", signup, name="signup"),
]
