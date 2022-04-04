from django.db import models

ATTENDANCE_TYPE_CHOICE = (
    ("S", "Suspended"),
    ("P", "Present"),
    ("A", "Absent"),
    ("L", "Leave"),
)


class ClassAttendance(models.Model):
    classroom = models.ForeignKey("Classroom", on_delete=models.CASCADE)
    # faculty who actually took the attendance
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "Class Attendance"

    def __str__(self):
        return f"{self.classroom.name}: {self.start_time} - {self.end_time}"


class StudentAttendance(models.Model):
    class_attendance = models.ForeignKey(ClassAttendance, on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    attendance = models.CharField(choices=ATTENDANCE_TYPE_CHOICE, max_length=10)
    comment = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        unique_together = [["class_attendance", "student"]]
        verbose_name_plural = "Student Attendance"

    def __str__(self):
        return f"{self.class_attendance.classroom.name}: {self.student.id} - {self.attendance}"
