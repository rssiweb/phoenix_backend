from django.db import models


class LanguageProficiency(models.Model):
    lang = models.ForeignKey("Language", on_delete=models.CASCADE)
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    speak = models.BooleanField(default=False)


class Language(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
