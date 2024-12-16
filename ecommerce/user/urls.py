from django.urls import path
from .views import RegisterView, ManageUserView, CustomAuthToken

app_name = "user"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="me"),
    path("login/", CustomAuthToken.as_view(), name="login"),
]
