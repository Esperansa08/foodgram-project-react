from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", _("Пользователь")
        ADMIN = "admin", _("Администратор")

    username = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        max_length=254, unique=True, verbose_name="Электронная почта"
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="Права доступа",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def is_upperclass(self):
        return self.role in {
            self.Role.USER,
            self.Role.ADMIN,
        }

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == self.Role.USER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="subscriber",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="subscribing",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="Возможена только одна подписка на автора",
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
