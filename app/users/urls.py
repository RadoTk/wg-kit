from django.urls import path
from . import views
from .views import UserLoginView
from django.contrib.auth.views import LogoutView


app_name = "users"
urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('signup/', views.signup, name='signup'),
]
