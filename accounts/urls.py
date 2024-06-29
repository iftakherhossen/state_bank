from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserLogOutView, UserBankAccountView, UserBankAccountUpdateView, ChangePasswordView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogOutView.as_view(), name='logout'),
    path('profile/', UserBankAccountView.as_view(), name='profile'),
    path('edit-profile/', UserBankAccountUpdateView.as_view(), name='edit_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]