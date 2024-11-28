from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from .views import RegisterView, ManageUserView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="me"),
    path("login/", ObtainAuthToken.as_view(), name="login"),
]
