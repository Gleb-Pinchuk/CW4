from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from mailings.models import Mailing, MailingAttempt, Client


class Command(BaseCommand):
    help = 'Отправка рассылки через командную строку'


    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительная отправка, игнорируя проверку времени'
        )


    def handle(self, *args, **kwargs):
        mailing_id = kwargs['mailing_id']
        force = kwargs['force']

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Рассылка с ID {mailing_id} не найдена'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n Запуск рассылки ID {mailing_id}'))
        self.stdout.write(f'   Тема: {mailing.message.subject}')
        self.stdout.write(f'   Период: {mailing.start_time} - {mailing.end_time}')
        self.stdout.write(f'   Получателей: {mailing.recipients.count()}')

        # Проверяем, активна ли рассылка
        if not mailing.is_active and not force:
            self.stdout.write(
                self.style.WARNING('Рассылка отключена. Используйте --force для принудительной отправки.'))
            return

        # Проверяем время
        now = timezone.now()

        if now < mailing.start_time and not force:
            self.stdout.write(self.style.WARNING(
                f' Рассылка еще не готова к отправке. Начало: {mailing.start_time}'
            ))
            self.stdout.write(self.style.WARNING('   Используйте --force для принудительной отправки.'))
            return

        if now > mailing.end_time and not force:
            self.stdout.write(self.style.WARNING(
                f'Время для отправки рассылки истекло. Окончание: {mailing.end_time}'
            ))
            self.stdout.write(self.style.WARNING('   Используйте --force для принудительной отправки.'))
            return

        if force:
            self.stdout.write(self.style.WARNING('Принудительная отправка (проверка времени отключена)'))

        self.stdout.write(self.style.SUCCESS('\n Начинаем отправку...\n'))

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
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Успешно отправлено: {client.email}'
                ))

            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='failed',
                    server_response=str(e)
                )
                failed_count += 1
                self.stdout.write(self.style.ERROR(
                    f' Ошибка при отправке {client.email}: {str(e)}'
                ))

        # Итоговая статистика
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS(' Итоговая статистика:'))
        self.stdout.write(self.style.SUCCESS(f'   Успешно: {success_count}'))
        self.stdout.write(self.style.ERROR(f'   Неудачно: {failed_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Всего: {success_count + failed_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 50 + '\n'))

        self.stdout.write(self.style.SUCCESS(' Рассылка завершена!'))
