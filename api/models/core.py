from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.attendance import StudentAttendance


class Branch(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # location attributes can be added here

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class Session(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = _("Sessions")

    def __str__(self):
        return self.name


class Quarter(models.Model):
    name = models.CharField(max_length=50)
    start = models.DateField()
    end = models.DateField()
    session = models.ForeignKey("Session", on_delete=models.CASCADE)

    class Meta:
        unique_together = [["name", "session"]]


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = _("Subjects")

    def __str__(self):
        return self.name


class BranchSessionAssociation(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    is_active = models.BooleanField(_("active"), default=False)

    class Meta:
        unique_together = [["branch", "session"]]

    def __str__(self):
        return f"{self.branch.name} ({self.session.name})"


class Category(models.Model):
    name = models.CharField(max_length=10, unique=True)
    branch = models.ForeignKey("Branch", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Categories")
        unique_together = [["name", "branch"]]

    def __str__(self):
        return self.name


class CategorySessionAssociation(models.Model):
    """to select operational categories in a session"""

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    subjects = models.ManyToManyField("Subject", through="CategorySubjectAssociation")
    students = models.ManyToManyField("Student", through="CategoryStudentAssociation")

    class Meta:
        verbose_name_plural = "Categories in Session"
        unique_together = [["category", "session"]]

    def __str__(self):
        return f"{self.bsa} - {self.category}"


class CategorySubjectAssociation(models.Model):
    cba = models.ForeignKey(CategorySessionAssociation, on_delete=models.CASCADE)
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)


class CategoryStudentAssociation(models.Model):
    cba = models.ForeignKey(CategorySessionAssociation, on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)


class Classroom(models.Model):
    bsa = models.ForeignKey("BranchSessionAssociation", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    sec_faculty = models.ForeignKey(
        "Faculty", on_delete=models.CASCADE, related_name="sec_classrooms", null=True, blank=True,
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # classes may not be on all days
    # 0010101 - tuesday, thursday and Saturday (SMTWTFS)
    working_days = models.CharField(max_length=7)
    grade_system = models.ForeignKey("GradeSystem", on_delete=models.CASCADE)
    students = models.ManyToManyField("Student", through="StudentClassroomAssociation")

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name


class StudentClassroomAssociation(models.Model):
    classroom = models.ForeignKey("Classroom", on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    attendance = models.BooleanField(
        default=True, help_text="Should this student be considers while taking attendance ?",
    )
    test = models.BooleanField(
        default=True, help_text="Should this student be considers while taking tests?",
    )
