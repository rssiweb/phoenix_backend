from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Badge(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    icon = models.CharField(max_length=512, null=True, blank=True)


class UserBadges(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    badge = models.ForeignKey("Badge", on_delete=models.CASCADE)
    assigned_on = models.DateTimeField(_("assigned on"), default=timezone.now)
    assigned_for = models.TextField(null=True, blank=True)
