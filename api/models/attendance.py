from django.utils import timezone
from django.db import models

from api.utils import safe_date_format

ATTENDANCE_TYPE_CHOICE = (
    ("S", "Suspended"),
    ("P", "Present"),
    ("A", "Absent"),
    ("L", "Leave"),
)


class ClassOccurrence(models.Model):
    classroom = models.ForeignKey("Classroom", on_delete=models.CASCADE)
    # faculty who actually took the class
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Class Occurrence"

    def __str__(self):
        start = safe_date_format(self.start_time, "%Y-%m-%d %H:%M")
        end = safe_date_format(self.end_time, "%Y-%m-%d %H:%M")
        return f"{self.classroom.name}: {start} - {end}"


class StudentAttendance(models.Model):
    class_occurrance = models.ForeignKey(ClassOccurrence, on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    # faculty who took the attendance
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    attendance = models.CharField(choices=ATTENDANCE_TYPE_CHOICE, max_length=1)
    comment = models.CharField(max_length=15, null=True, blank=True)
    entry_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [["class_occurrance", "student"]]
        verbose_name_plural = "Student Attendance"

    def __str__(self):
        return f"{self.class_occurrance.classroom.name}: {self.student.id} - {self.attendance}"
