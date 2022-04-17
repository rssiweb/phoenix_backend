from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from api.constants import USER_TYPE_STUDENT, USER_TYPE_ADMIN, USER_TYPE_FACULTY

GENDER_CHOICES = (
    (1, _("Male")),
    (2, _("Female")),
    (3, _("Others")),
)


USER_TYPE_CHOICES = (
    (USER_TYPE_STUDENT, _("Student")),
    (USER_TYPE_FACULTY, _("Faculty")),
    (USER_TYPE_ADMIN, _("Admin")),
)


class User(AbstractUser):
    type = models.PositiveSmallIntegerField(
        _("user type"), choices=USER_TYPE_CHOICES, null=True, blank=True
    )
    profile_pic = models.CharField(_("profile picture"), max_length=512, null=True, blank=True)
    phone = models.CharField(max_length=512, null=True, blank=True)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    dob = models.DateField(
        _("date of birth"), auto_now=False, auto_now_add=False, null=True, blank=True,
    )
    inactive_from = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return f"{self.username}"


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(
        _("preferred title"),
        max_length=50,
        null=True,
        blank=True,
        help_text=_("how would you like to be addressed"),
    )
    permanent_address = models.CharField(max_length=200, null=True, blank=True)
    current_address = models.CharField(max_length=200, null=True, blank=True)
    languages = models.ManyToManyField("Language", through="LanguageProficiency")
    base_branch = models.ForeignKey("Branch", on_delete=models.CASCADE)
    work_experience = models.TextField()

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return self.user.username


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    # class
    # gardian_name
    # relation_with_student
    # aadhaar
    # gardian_aadhaar
    # postal_address
    # subjects
    # preferred_branch
    # school_name
    # board_name
    # state
    # school_admission_required
    # status

    # session = models.ForeignKey("Session", on_delete=models.CASCADE)

    # actual_class = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Students"
        # students will be copied to new sessions hence student_id cannot be unique
        # unique_together = [["profile", "session"]]

    def __str__(self):
        return self.user.username
