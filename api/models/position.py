from django.db import models


class UserPosition(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    position = models.ForeignKey("Position", on_delete=models.CASCADE)
    approved_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name="positions_approved")


class Position(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
