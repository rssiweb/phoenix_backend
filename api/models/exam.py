from django.db import models


class Exam(models.Model):
    bsa = models.ForeignKey("BranchSessionAssociation", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)

    class Meta:
        unique_together = [["name", "bsa"]]

    def __str__(self):
        return f"({self.session.branch.name}, {self.session.name}): {self.name}"


class Test(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    classroom = models.ForeignKey("Classroom", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date = models.DateField(auto_now=False, auto_now_add=False)
    max_marks = models.FloatField()
    evaluator = models.ForeignKey("Faculty", on_delete=models.CASCADE)

    def __str__(self):
        f"{self.exam.name}: {self.name}"


class Mark(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    mark = models.FloatField()
    comment = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        f"{self.test.name}: {self.mark}"
