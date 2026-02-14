from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class UserRegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя"""

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserProfileForm(UserChangeForm):
    """Форма профиля пользователя"""

    password = None  # Скрываем поле пароля

    class Meta:
        model = User
        fields = ('email', 'avatar', 'phone', 'country')
