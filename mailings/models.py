from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from users.models import User


class Client(models.Model):
    """Получатель рассылки (клиент)"""

    email = models.EmailField(
        _('Email'),
        unique=True,
        validators=[EmailValidator()],
        help_text=_('Уникальный адрес электронной почты')
    )

    full_name = models.CharField(
        _('Ф.И.О.'),
        max_length=255,
        help_text=_('Полное имя получателя')
    )

    comment = models.TextField(
        _('Комментарий'),
        blank=True,
        null=True,
        help_text=_('Дополнительная информация о получателе')
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name=_('Владелец')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Получатель рассылки')
        verbose_name_plural = _('Получатели рассылок')
        ordering = ['email']
        permissions = [
            ('view_all_clients', _('Может просматривать всех клиентов')),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    """Сообщение для рассылки"""

    subject = models.CharField(
        _('Тема письма'),
        max_length=255,
        help_text=_('Тема письма')
    )

    body = models.TextField(
        _('Тело письма'),
        help_text=_('Содержание письма')
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Владелец')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Сообщение')
        verbose_name_plural = _('Сообщения')
        ordering = ['-created_at']
        permissions = [
            ('view_all_messages', _('Может просматривать все сообщения')),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Рассылка"""

    STATUS_CHOICES = [
        ('created', _('Создана')),
        ('running', _('Запущена')),
        ('completed', _('Завершена')),
    ]

    start_time = models.DateTimeField(
        _('Дата и время начала отправки'),
        help_text=_('С какого момента рассылка может быть запущена')
    )

    end_time = models.DateTimeField(
        _('Дата и время окончания отправки'),
        help_text=_('До какого момента разрешено выполнять отправку')
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name=_('Сообщение'),
        help_text=_('Какое письмо будет отправлено в рассылке')
    )

    recipients = models.ManyToManyField(
        Client,
        related_name='mailings',
        verbose_name=_('Получатели'),
        help_text=_('Список клиентов, которые получат данную рассылку')
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name=_('Владелец')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Рассылка')
        verbose_name_plural = _('Рассылки')
        ordering = ['-created_at']
        permissions = [
            ('view_all_mailings', _('Может просматривать все рассылки')),
            ('deactivate_mailing', _('Может отключать рассылки')),
            ('view_statistics', _('Может просматривать статистику')),
        ]

    def __str__(self):
        return f"Рассылка от {self.start_time} до {self.end_time}"

    def get_status(self):
        """Динамический расчет статуса рассылки"""
        now = timezone.now()

        if now < self.start_time:
            return 'created'
        elif self.start_time <= now <= self.end_time:
            return 'running'
        else:
            return 'completed'

    @property
    def status_display(self):
        """Отображение статуса на русском"""
        status_dict = dict(self.STATUS_CHOICES)
        return status_dict.get(self.get_status(), _('Неизвестно'))


class MailingAttempt(models.Model):
    """Попытка рассылки"""

    STATUS_CHOICES = [
        ('success', _('Успешно')),
        ('failed', _('Не успешно')),
    ]

    attempt_time = models.DateTimeField(
        _('Дата и время попытки'),
        auto_now_add=True
    )

    status = models.CharField(
        _('Статус'),
        max_length=10,
        choices=STATUS_CHOICES
    )

    server_response = models.TextField(
        _('Ответ почтового сервера'),
        blank=True,
        null=True
    )

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('Рассылка')
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attempts',
        verbose_name=_('Получатель')
    )

    class Meta:
        verbose_name = _('Попытка рассылки')
        verbose_name_plural = _('Попытки рассылок')
        ordering = ['-attempt_time']


    def __str__(self):
        return f"Попытка от {self.attempt_time} - {self.status}"
