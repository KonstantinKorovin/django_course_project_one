from django.core.exceptions import ValidationError
from django.db import models

from communications.models import Message
from users.models import CustomUser, Recipient

FINISHED = "finished"
CREATED = "created"
LAUNCHED = "launched"
SUCCESS = "success"
NOT_SUCCESS = "not success"


STATUS_CHOICES = [
    (FINISHED, "Закончена"),
    (CREATED, "Создана"),
    (LAUNCHED, "Запущена"),
]

ATTEMPT_STATUS_CHOICES = [
    (SUCCESS, "Успешно"),
    (NOT_SUCCESS, "Не успешно"),
]


class Mailing(models.Model):
    """Модель 'Рассылка'"""

    first_date_mailing = models.DateTimeField()
    end_date_mailing = models.DateTimeField()
    status = models.CharField(
        default=CREATED, choices=STATUS_CHOICES, verbose_name="Статус рассылки"
    )
    message = models.ForeignKey(
        to=Message, on_delete=models.CASCADE, null=True, blank=True
    )
    recipients = models.ManyToManyField(to=Recipient)
    owner = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Владелец рассылки",
        blank=True,
        null=True,
    )

    def clean(self):
        if self.end_date_mailing <= self.first_date_mailing:
            raise ValidationError(
                "Дата окончания отправки должна быть позже даты первой отправки."
            )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

        permissions = [
            ("can_view_all_mailings", "Can view all mailings"),
            ("can_disable_mailing", "Can disable a mailing"),
        ]


class MailingAttempt(models.Model):
    """Модель 'Попытка рассылки'"""

    date_attempt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=ATTEMPT_STATUS_CHOICES, verbose_name="Статус отправки рассылки"
    )
    response_status = models.TextField(verbose_name="Ответ почтового сервера")
    mailing = models.ForeignKey(to=Mailing, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
