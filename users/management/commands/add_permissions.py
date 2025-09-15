from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from communications.models import Message
from mailings.models import Mailing
from users.models import Recipient


class Command(BaseCommand):

    help = " Команда для создания прав на добавление для новых объектов "

    def handle(self, *args, **kwargs):
        content_type_mailing = ContentType.objects.get_for_model(Mailing)
        content_type_recipient = ContentType.objects.get_for_model(Recipient)
        content_type_message = ContentType.objects.get_for_model(Message)

        if not Permission.objects.filter(codename="add_mailing").exists():
            Permission.objects.create(
                codename="add_mailing",
                name="Can add mailing",
                content_type=content_type_mailing,
            )

        if not Permission.objects.filter(codename="add_recipient").exists():
            Permission.objects.create(
                codename="add_recipient",
                name="Can add recipient",
                content_type=content_type_recipient,
            )

        if not Permission.objects.filter(codename="add_message").exists():
            Permission.objects.create(
                codename="add_message",
                name="Can add message",
                content_type=content_type_message,
            )

        self.stdout.write(self.style.SUCCESS("Permissions have been created."))
