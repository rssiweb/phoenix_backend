from django.db import models


class GradeSystem(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE)
    name = models.CharField(max_length=20)


class Grade(models.Model):
    grade_system = models.ForeignKey(GradeSystem, on_delete=models.CASCADE)
    low = models.FloatField()
    high = models.FloatField()
    grade = models.CharField(max_length=5)
    description = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.grade} ({self.low}-{self.high})"
