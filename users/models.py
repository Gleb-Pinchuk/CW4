from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractUser):
    """Кастомная модель пользователя"""

    username = None

    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Must be a valid email address.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Номер телефона')
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Страна')
    )

    is_blocked = models.BooleanField(
        default=False,
        verbose_name=_('Заблокирован')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['email']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Приводим email к нижнему регистру при сохранении"""
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)