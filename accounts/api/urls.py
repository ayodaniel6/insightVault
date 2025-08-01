from django.urls import path
from .views_api import (
    RegisterView, LoginView, ProfileView,
    ChangePasswordView, DeleteAccountView, 
    PasswordResetRequestView, PasswordResetConfirmView
)

app_name = "accounts_api"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("delete/", DeleteAccountView.as_view(), name="delete_account"),
    path("forgot-password/", PasswordResetRequestView.as_view(), name="forgot_password"),
    path("reset-password/", PasswordResetConfirmView.as_view(), name="reset_password"),
]
