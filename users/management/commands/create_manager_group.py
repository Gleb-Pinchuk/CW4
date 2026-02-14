from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Mailing, Client, Message


class Command(BaseCommand):
    help = 'Создает группу менеджеров с необходимыми правами'

    def handle(self, *args, **kwargs):
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Менеджеры" уже существует'))

        mailing_content_type = ContentType.objects.get_for_model(Mailing)
        client_content_type = ContentType.objects.get_for_model(Client)
        message_content_type = ContentType.objects.get_for_model(Message)

        view_mailing = Permission.objects.get(codename='view_mailing', content_type=mailing_content_type)
        view_client = Permission.objects.get(codename='view_client', content_type=client_content_type)
        view_message = Permission.objects.get(codename='view_message', content_type=message_content_type)

        manager_group.permissions.add(view_mailing, view_client, view_message)

        self.stdout.write(self.style.SUCCESS('Права для менеджеров настроены успешно!'))
        self.stdout.write(self.style.SUCCESS('Чтобы назначить пользователя менеджером:'))
        self.stdout.write(self.style.SUCCESS('1. Зайдите в админку (/admin/)'))
        self.stdout.write(self.style.SUCCESS('2. Перейдите в раздел "Пользователи"'))
        self.stdout.write(self.style.SUCCESS('3. Выберите пользователя'))
        self.stdout.write(self.style.SUCCESS('4. В разделе "Группы" выберите "Менеджеры"'))
