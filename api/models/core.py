from django.db import models
from django.contrib.auth.models import User
import pytz


# ((timezone, timezone) for timezone in pytz.all_timezones)
TIMEZONE_CHOICES = (("Asia/Kolkata", "Asia/Kolkata"),)


class Branch(models.Model):
    name = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES)
    # location attributes can be added here

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Sessions"

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"


class BranchSessionAssociation(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    is_active = models.BooleanField()

    class Meta:
        verbose_name_plural = "Session for Branch"
        unique_together = [["branch", "session"]]

    def __str__(self):
        return f"{self.branch.name} ({self.session.name})"


class CategoryBranchAssociation(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    bsa = models.ForeignKey(BranchSessionAssociation, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["category", "bsa"]]

    def __str__(self):
        return f"{self.category} - {self.subject}"


class CategorySubjectAssociation(models.Model):
    cba = models.ForeignKey(CategoryBranchAssociation, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)


class CategoryStudentAssociation(models.Model):
    cba = models.ForeignKey(CategoryBranchAssociation, on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)


class Classroom(models.Model):
    name = models.CharField(max_length=20)
    bsa = models.ForeignKey(BranchSessionAssociation, on_delete=models.CASCADE)
    # to identify students under this class
    cbas = models.ManyToManyField(CategoryBranchAssociation)

    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    # case when the faculty is not able to take the class
    sec_faculty = models.ForeignKey(
        "Faculty",
        on_delete=models.CASCADE,
        related_name="sec_classrooms",
        null=True,
        blank=True,
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # classes may not be on all days
    # 0010101 - tuesday, thursday and Saturday (SMTWTFS)
    working_days = models.CharField(max_length=7)
    # students to be excluded from attendance
    exclude_from_class = models.ManyToManyField(
        "Student", related_name="exclude_from_classes_for_attendance", blank=True,
    )
    # students to be excluded from test
    exclude_from_test = models.ManyToManyField(
        "Student", related_name="exclude_from_classes_for_test", blank=True
    )
    grade_system = models.ForeignKey("GradeSystem", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.name}"

