from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, UserProfileForm


class RegisterView(CreateView):
    """Регистрация нового пользователя"""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        messages.success(self.request, 'Регистрация прошла успешно! Теперь вы можете войти.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    """Профиль пользователя"""
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)


def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_blocked:
                messages.error(request, 'Ваш аккаунт заблокирован. Обратитесь к администратору.')
                return render(request, 'users/login.html')

            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.email}!')
            return redirect('mailings:index')
        else:
            messages.error(request, 'Неверный email или пароль.')

    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('mailings:index')
