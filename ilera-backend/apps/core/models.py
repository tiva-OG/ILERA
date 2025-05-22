from django.db import models
from .fields import ULIDField


class ULIDModel(models.Model):
    id = ULIDField()

    class Meta:
        abstract = True
