from django.core.management import BaseCommand

from mailings.models import Mailing
from mailings.tasks import send_mailing_to_recipients


class Command(BaseCommand):
    help = "Кастомная команда для запуска рассылки"

    def add_arguments(self, parser):
        parser.add_argument("pk", type=int, help="ID рассылки")

    def handle(self, *args, **options):
        mailing_pk = options["pk"]

        try:
            send_mailing_to_recipients(mailing_pk)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Рассылка по ключу '{mailing_pk}' успешно отправлена получателям."
                )
            )
        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"Рассылка по ключу '{mailing_pk}' не существует, проверьте правильность ключа."
                )
            )
            return
