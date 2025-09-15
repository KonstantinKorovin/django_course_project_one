from email.headerregistry import Group

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from mailings.models import Mailing
from users.models import CustomUser, Recipient


class Command(BaseCommand):

    help = " Команда для создания группы 'Менеджеры' и присвоения ей необходимых прав "

    def handle(self, *args, **options):

        managers_group, created = Group.objects.get_or_create(name="Managers")
        self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' созданa."))

        can_view_all_mailings, _ = Permission.objects.get_or_create(
            codename="can_view_all_mailings",
            content_type=ContentType.objects.get_for_model(Mailing),
        )
        can_disable_mailing, _ = Permission.objects.get_or_create(
            codename="can_disable_mailing",
            content_type=ContentType.objects.get_for_model(Mailing),
        )
        can_view_all_recipients, _ = Permission.objects.get_or_create(
            codename="can_view_all_recipients",
            content_type=ContentType.objects.get_for_model(Recipient),
        )
        can_block_user, _ = Permission.objects.get_or_create(
            codename="can_block_user",
            content_type=ContentType.objects.get_for_model(CustomUser),
        )
        view_user, _ = Permission.objects.get_or_create(
            codename="view_user",
            content_type=ContentType.objects.get_for_model(CustomUser),
        )

        managers_group.permissions.add(
            can_view_all_mailings,
            can_disable_mailing,
            can_view_all_recipients,
            can_block_user,
            view_user,
        )

        self.stdout.write(
            self.style.SUCCESS("Все права успешно присвоены группе 'Менеджеры'.")
        )
