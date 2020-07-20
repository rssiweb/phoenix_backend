from django.contrib import admin
from api.models import (
    Branch,
    Session,
    Subject,
    Category,
    UserProfile,
    Faculty,
    Student,
    GradeSystem,
    Grade,
    Classroom,
    Leave,
    ClassAttendance,
    StudentAttendance,
    Exam,
    Test,
    Mark,
)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("branch", "name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_filter = ("session__name",)
    list_display = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ("session__name",)
    list_display = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "profile_id",
        "profile_pic",
        "phone",
        "gender",
        "dob",
        "inactive_from",
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_filter = ("branch__name",)
    list_display = ("profile", "branch")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_filter = ("session__name",)
    list_display = (
        "profile",
        "category",
    )


@admin.register(GradeSystem)
class GradeSystemAdmin(admin.ModelAdmin):
    list_filter = ("session__name",)
    list_display = ("session", "name")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_filter = ("grade_system__name",)
    list_display = ("grade_system", "low", "high", "grade", "description")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    def category_names(self, obj):
        return f"{','.join([cat.name for cat in obj.categories.all()])}"

    def students_excluded_from_attendance(self, obj):
        return f"{','.join([student.id for student in obj.exluded_from_class.all()])}"

    def students_excluded_from_test(self, obj):
        return f"{','.join([student.id for student in obj.exluded_from_test.all()])}"

    list_filter = ("session__name",)
    list_display = (
        "name",
        "category_names",
        "faculty",
        "sec_faculty",
        "subject",
        "working_days",
        "students_excluded_from_attendance",
        "students_excluded_from_test",
        "grade_system",
    )


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("student", "from_date", "to_date", "type")


@admin.register(ClassAttendance)
class ClassAttendanceAdmin(admin.ModelAdmin):
    list_display = ("classroom", "faculty", "start_time", "end_time")


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ("class_attendance", "student", "attendance", "comment")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_filter = ("session__name",)
    list_display = ("name", "start_date", "end_date")


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_filter = ("exam__name",)
    list_display = ("classroom", "name", "date", "max_marks", "evaluator")


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_filter = ("test__name",)
    list_display = ("test", "student", "mark", "comment")
