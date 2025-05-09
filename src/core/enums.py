from django.db import models


class ConditionEnums(models.TextChoices):
    USED = 'used', 'Б/У'
    NEW = 'new', 'Новое'


class StatusEnums(models.TextChoices):
    WAITING = 'waiting', 'Ожидание'
    ACCEPTED = 'accepted', 'Приняли'
    REJECTED = 'rejected', 'Отклонили'
