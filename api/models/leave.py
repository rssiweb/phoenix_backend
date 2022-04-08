from django.db import models

LEAVE_TYPE_CHOICES = (("full", "Full day leave"),)


class Leave(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    from_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    to_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES, null=False)

    def __str__(self):
        return f"{self.user.id}: {self.from_date}-{self.to_date}"
