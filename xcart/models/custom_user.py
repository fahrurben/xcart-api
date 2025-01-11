from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    class UserRoles(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        USER = 'staff', _('User')

    role = models.CharField(
        max_length=11,
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'role')

    def __str__(self):
        return self.email

    def following(self, user):
        return self.follows_by.filter(id=user.id).exists()