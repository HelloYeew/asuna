from django.contrib.auth.models import User
from django.db import models


THEME_SETTINGS = (
    ('', 'Default'),
    ('green', 'Green')
)


class Settings(models.Model):
    """Settings model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, choices=THEME_SETTINGS, default='', blank=True)

    class Meta:
        """Meta class."""

        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'

    def __str__(self):
        """Return name."""
        return self.user.username + ' settings'
