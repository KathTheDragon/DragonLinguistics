from django.contrib.auth.models import AbstractUser

class UpdatableModel(models.Model):
    updated_at = models.DateTimeField(
        auto_now=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True


class User(UpdatableModel, AbstractUser):
    pass
