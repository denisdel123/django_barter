from django.db import models
from core import constants, enums
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(
        max_length=constants.MAX_LENGTH_CATEGORY,
        verbose_name="Название"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Ads(models.Model):
    title = models.CharField(
        max_length=constants.MAX_LENGTH_ADS,
        verbose_name="Название"
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    image_url = models.URLField(
        **constants.NULLABLE,
        verbose_name="Ссылка на фото"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категории",
        related_name="ads"
    )
    condition = models.CharField(
        max_length=constants.MAX_LENGTH_CHOICES,
        choices=enums.ConditionEnums.choices,
        verbose_name="Состояние"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="abs",
        **constants.NULLABLE
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class ExchangeProposal(models.Model):
    ad_sender = models.ForeignKey(
        Ads,
        on_delete=models.CASCADE,
        verbose_name="Объявление отправителя",
        related_name="sent_exchange_proposals"
    )
    ad_receiver = models.ForeignKey(
        Ads,
        on_delete=models.CASCADE,
        verbose_name="Объявление получателя",
        related_name="received_exchange_proposals"
    )
    comment = models.CharField(
        max_length=constants.MAX_LENGTH_CHOICES,
        verbose_name="Комментарий",
        **constants.NULLABLE
    )
    status = models.CharField(
        max_length=constants.MAX_LENGTH_CHOICES,
        choices=enums.StatusEnums.choices,
        default=enums.StatusEnums.WAITING,
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата Обновления"
    )

    def __str__(self):
        return f"Статус: {self.status} Отправитель: {self.ad_sender.owner} Получатель: {self.ad_receiver.owner}"

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"
