from django.db import models

from users.models import CustomUser


class Message(models.Model):
    """Модель 'Сообщение'"""

    theme = models.CharField(max_length=255, verbose_name="Тема письма")
    message = models.TextField(blank=True, null=True, verbose_name="Текст письма")
    owner = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Создатель сообщения",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
