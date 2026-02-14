from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from django.core.cache import cache
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from users.models import User


class IndexView(LoginRequiredMixin, ListView):
    """Главная страница"""
    template_name = 'mailings/index.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        cache_key = f'main_stats_{self.request.user.id}'
        stats = cache.get(cache_key)

        if stats is None:
            if self.request.user.groups.filter(name='Менеджеры').exists():
                total_mailings = Mailing.objects.count()
                active_mailings = Mailing.objects.filter(
                    start_time__lte=timezone.now(),
                    end_time__gte=timezone.now(),
                    is_active=True
                ).count()
            else:
                total_mailings = Mailing.objects.filter(owner=self.request.user).count()
                active_mailings = Mailing.objects.filter(
                    owner=self.request.user,
                    start_time__lte=timezone.now(),
                    end_time__gte=timezone.now(),
                    is_active=True
                ).count()

            total_clients = Client.objects.count()

            stats = {
                'total_mailings': total_mailings,
                'active_mailings': active_mailings,
                'total_clients': total_clients,
            }

            cache.set(cache_key, stats, 300)  # 5 минут

        self.extra_context = stats
        return Mailing.objects.filter(owner=self.request.user).order_by('-created_at')[:5]


class ClientListView(LoginRequiredMixin, ListView):
    """Список клиентов"""
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Создание клиента"""
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Клиент успешно создан!')
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование клиента"""
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:client_list')

    def test_func(self):
        client = self.get_object()
        return client.owner == self.request.user or self.request.user.groups.filter(name='Менеджеры').exists()

    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно обновлен!')
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление клиента"""
    model = Client
    template_name = 'mailings/client_confirm_delete.html'
    success_url = reverse_lazy('mailings:client_list')

    def test_func(self):
        client = self.get_object()
        return client.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Клиент успешно удален!')
        return super().delete(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, ListView):
    """Список сообщений"""
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def test_func(self):
        message = self.get_object()
        return message.owner == self.request.user or self.request.user.groups.filter(name='Менеджеры').exists()

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено!')
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление сообщения"""
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')

    def test_func(self):
        message = self.get_object()
        return message.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Сообщение успешно удалено!')
        return super().delete(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, ListView):
    """Список рассылок"""
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Детали рассылки"""
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def test_func(self):
        mailing = self.get_object()
        return mailing.owner == self.request.user or self.request.user.groups.filter(name='Менеджеры').exists()


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        mailing = self.get_object()
        return mailing.owner == self.request.user or self.request.user.groups.filter(name='Менеджеры').exists()

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно обновлена!')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление рассылки"""
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def test_func(self):
        mailing = self.get_object()
        return mailing.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Рассылка успешно удалена!')
        return super().delete(request, *args, **kwargs)


@login_required
def send_mailing_view(request, pk):
    """Запуск рассылки через интерфейс"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверяем права доступа
    if mailing.owner != request.user and not request.user.groups.filter(name='Менеджеры').exists():
        messages.error(request, 'У вас нет прав для запуска этой рассылки.')
        return redirect('mailings:mailing_list')

    # Проверяем, активна ли рассылка
    if not mailing.is_active:
        messages.error(request, 'Рассылка отключена.')
        return redirect('mailings:mailing_list')

    # Проверяем время
    now = timezone.now()
    if now < mailing.start_time:
        messages.error(request, f'Рассылка еще не готова к отправке. Начало: {mailing.start_time}')
        return redirect('mailings:mailing_list')

    if now > mailing.end_time:
        messages.error(request, f'Время для отправки рассылки истекло. Окончание: {mailing.end_time}')
        return redirect('mailings:mailing_list')

    # Отправляем письма
    success_count = 0
    failed_count = 0

    for client in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status='success',
                server_response='Email sent successfully'
            )
            success_count += 1

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status='failed',
                server_response=str(e)
            )
            failed_count += 1

    messages.success(
        request,
        f'Рассылка выполнена! Успешно: {success_count}, Неудачно: {failed_count}'
    )

    return redirect('mailings:mailing_detail', pk=pk)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список попыток рассылок"""
    model = MailingAttempt
    template_name = 'mailings/attempts_list.html'
    context_object_name = 'attempts'
    ordering = ['-attempt_time']

    def get_queryset(self):
        if self.request.user.groups.filter(name='Менеджеры').exists():
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)
