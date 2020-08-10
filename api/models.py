from django.db import models
from django.contrib.auth.models import User
import pytz

# choices
GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("others", "Others"),
)

LEAVE_TYPE_CHOICES = (("full", "Full day leave"),)

ATTENDANCE_TYPE_CHOICE = (
    ("S", "Suspended"),
    ("P", "Present"),
    ("A", "Absent"),
    ("L", "Leave"),
)

TIMEZONE_CHOICES = ((timezone, timezone) for timezone in pytz.all_timezones)


class Branch(models.Model):
    name = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class Session(models.Model):
    is_active = models.BooleanField()
    name = models.CharField(max_length=50)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["name", "branch"]]

    def __str__(self):
        return f"{self.branch.name}: {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=50)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["name", "session"]]

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.name}"


class Category(models.Model):
    name = models.CharField(max_length=10)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["name", "session"]]
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.name}"


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
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.profile.profile_id}"


class Student(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    actual_class = models.CharField(max_length=20)

    class Meta:
        # students will be copied to new sessions hence student_id cannot be unique
        unique_together = [["profile", "session"]]

    def __str__(self):
        return f"({self.profile.id}, {self.session.name}): {self.category.id}"


class GradeSystem(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)


class Grade(models.Model):
    grade_system = models.ForeignKey(GradeSystem, on_delete=models.CASCADE)
    low = models.FloatField()
    high = models.FloatField()
    grade = models.CharField(max_length=5)
    description = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.grade} ({self.low}-{self.high})"


class Classroom(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    categories = models.ManyToManyField(Category)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    # case when the faculty is not able to take the class
    sec_faculty = models.ForeignKey(
        Faculty,
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
    exluded_from_class = models.ManyToManyField(
        Student, related_name="exclude_from_classes_for_attendance", blank=True,
    )
    # students to be excluded from test
    exluded_from_test = models.ManyToManyField(
        Student, related_name="exclude_from_classes_for_test", blank=True
    )
    grade_system = models.ForeignKey(GradeSystem, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.name}"


class Leave(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    from_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    to_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES, null=False)

    def __str__(self):
        return f"{self.student.id}: {self.from_date}-{self.to_date}"


class ClassAttendance(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    # faculty who actually took the attendance
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Class Attendance"

    def __str__(self):
        return f"{self.classroom.name}: {self.start_time}-{self.end_time}"


class StudentAttendance(models.Model):
    class_attendance = models.ForeignKey(ClassAttendance, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.CharField(choices=ATTENDANCE_TYPE_CHOICE, max_length=10)
    comment = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        unique_together = [["class_attendance", "student"]]
        verbose_name_plural = "Student Attendance"

    def __str__(self):
        return f"{self.class_attendance.classroom.name}: {self.student.id} - {self.attendance}"


# examination related models
class Exam(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)

    class Meta:
        unique_together = [["name", "session"]]

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.name}"


class Test(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date = models.DateField(auto_now=False, auto_now_add=False)
    max_marks = models.FloatField()
    evaluator = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        f"{self.exam.name}: {self.name}"


class Mark(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    mark = models.FloatField()
    comment = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        f"{self.test.name}: {self.mark}"
