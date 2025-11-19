from django.urls import path
from app.users.views import UserLoginView, signup, user_logout, profile_edit, address_list, address_add, address_edit


app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"),
    path("signup/", signup, name="signup"),

    # Profil
    path("profile/edit/", profile_edit, name="profile_edit"),

    # Adresses
    path("addresses/", address_list, name="address_list"),
    path("addresses/add/", address_add, name="address_add"),
    path("addresses/<int:pk>/edit/", address_edit, name="address_edit"),
]
