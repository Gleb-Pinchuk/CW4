from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('email', 'full_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('subject',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner', 'start_time', 'end_time', 'is_active')
    list_filter = ('owner', 'start_time', 'end_time', 'is_active')
    search_fields = ('message__subject',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'client', 'attempt_time', 'status')
    list_filter = ('status', 'attempt_time', 'mailing')
    search_fields = ('server_response',)
