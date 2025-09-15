from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="e-mail пользователя")
    avatar = models.ImageField(
        upload_to="images/users/photo/",
        default="images/users/photo/img.png",
        verbose_name="Фотография пользователя",
    )
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Телефон пользователя"
    )
    country = models.CharField(
        max_length=35, blank=True, null=True, verbose_name="Страна пользователя"
    )
    token = models.CharField(max_length=100, unique=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email

    class Meta:
        permissions = [("can_block_user", "Can block users")]


class Recipient(models.Model):
    """Модель 'Получатель рассылок'"""

    email = models.EmailField(unique=True, verbose_name="Почта")
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    owner = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Создатель получателя",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [("can_view_all_recipients", "Can view all recipients")]
