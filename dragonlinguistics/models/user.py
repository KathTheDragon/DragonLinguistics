from django.contrib.auth.models import AbstractUser

from .base.abstracts import UpdatableModel


class User(UpdatableModel, AbstractUser):
    pass
