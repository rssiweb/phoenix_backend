from django.db import models
from django.contrib.auth.models import User
import pytz


GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("others", "Others"),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_id = models.CharField(max_length=15, unique=True, null=False, blank=False)
    profile_pic = models.CharField(max_length=512, null=True, blank=True)
    phone = models.CharField(max_length=512, null=True, blank=True)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, null=True, blank=True
    )
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    inactive_from = models.DateField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )

    def __str__(self):
        return f"{self.profile_id}"


class Faculty(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    # just to identify where the faculty joined
    # this does not restrict a faculty's ability to work in/for any other branch
    base_branch = models.ForeignKey("Branch", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.profile.profile_id}"


class Student(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # session = models.ForeignKey("Session", on_delete=models.CASCADE)
    # category = models.ForeignKey("Category", on_delete=models.CASCADE)
    # actual_class = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Students"
        # students will be copied to new sessions hence student_id cannot be unique
        # unique_together = [["profile", "session"]]

    def __str__(self):
        return f"({self.profile.id}"
