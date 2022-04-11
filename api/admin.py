from django.contrib import admin

from django.apps import apps
from api.models import Branch
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.admin import UserAdmin
from api.models.attendance import ClassOccurrence, StudentAttendance
from api.models.badge import Badge, UserBadges
from api.models.exam import Exam, Mark, Test
from api.models.language import Language, LanguageProficiency

from api.models.leave import Leave
from api.models.position import Position, UserPosition
from .models import User


from api.models.core import BranchSessionAssociation, Category, CategorySessionAssociation, CategoryStudentAssociation, CategorySubjectAssociation, Classroom, Quarter, Session, StudentClassroomAssociation, Subject
from api.models.grade import Grade, GradeSystem
from api.models.user import Faculty, Student

models = apps.get_models("api")

# model_names_to_register = [
#     "Branch",
#     "Session",
#     "Quarter",
#     "Subject",
#     "Category",
#     "StudentClassroomAssociation",
#     "SessionQuarterAssociation",
#     "BranchSessionAssociation",
#     "CategoryBranchAssociation",
#     "CategorySubjectAssociation",
#     "CategoryStudentAssociation",
#     "Classroom_cbas",
#     "Classroom_exclude_from_class",
#     "Classroom_exclude_from_test",
#     "Classroom",
#     "ClassOccurrance",
#     "StudentAttendance",
#     "Exam",
#     "Test",
#     "Mark",
#     "GradeSystem",
#     "Grade",
#     "Leave",
#     "Faculty",
#     "Student",
# ]

# models = [model for model in models if model.__name__ in model_names_to_register]

# for model in models:
#     admin.site.register(model)



@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_filter = ("type", "is_active")
    list_display = (
        "username",
        "email",
        "get_full_name",
        "is_staff",
        "type",
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "type",
                    "profile_pic",
                    "phone",
                    "gender",
                )
            },
        ),
        (
            _("Important dates"),
            {"fields": ("dob", "inactive_from", "last_login", "date_joined",)},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    # "user_permissions",
                ),
            },
        ),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name",)



@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Quarter)
class QuaterAdmin(admin.ModelAdmin):
    list_display = ("name","start","end","session")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    # list_filter = ("session__name",)
    list_display = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # list_filter = ("session__name",)
    list_display = ("name",)

@admin.register(BranchSessionAssociation)
class BranchSessionAssociationAdmin(admin.ModelAdmin):
    # list_filter = ("session__name",)
    list_display = ("branch","session","is_active")


@admin.register(CategorySubjectAssociation)
class CategorySubjectAssociationAdmin(admin.ModelAdmin):
    list_display = ("cba","subject",)

@admin.register(CategoryStudentAssociation)
class CategoryStudentAssociationnAdmin(admin.ModelAdmin):
    list_display = ("cba","student",)

@admin.register(CategorySessionAssociation)                            
class CategorySessionAssociationAdmin(admin.ModelAdmin):
    list_display = ("category","session",)      

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(LanguageProficiency)
class LanguageProficiencyAdmin(admin.ModelAdmin):
    list_display = ("lang","faculty","read","write","speak")   

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):  
    list_filter = ("base_branch",   
                )
    list_display = ("user",
                "title",
                "permanent_address",
                "current_address",
                "base_branch",
                "work_experience"
            )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # list_filter = ("session__name",)
    list_display = (
        "user",
        # "category",
    )


@admin.register(GradeSystem)
class GradeSystemAdmin(admin.ModelAdmin):
    # list_filter = ("session__name",)
    list_display = ("bsa", "name")


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

    # list_filter = ("session__name",)
    list_display = (
        "bsa",
        "name",
        "faculty",
        "sec_faculty",
        "subject",
        "working_days",
        "grade_system",
    )

# @admin.register(StudentClassroomAssociation)
# class StudentClassroomAssociationAdmin(admin.ModelAdmin):
#     list_display = ("classroom", "student")

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("user", "from_date", "to_date", "type")


@admin.register(ClassOccurrence)
class ClassOccurranceAdmin(admin.ModelAdmin):
    list_display = ("classroom", "faculty", "start_time", "end_time")


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_filter = ("attendance",)
    list_display = ("class_occurrance", "student","faculty", "attendance", "comment", "entry_on")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    # list_filter = ("session__name",)
    list_display = ("name", "start_date", "end_date")


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_filter = ("exam__name",)
    list_display = ("classroom", "name", "date", "max_marks", "evaluator")


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_filter = ("test__name",)
    list_display = ("test", "student", "mark", "comment")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name","icon")

@admin.register(UserBadges)
class UserBadgesAdmin(admin.ModelAdmin):
    list_display = ("user","badge","assigned_on","assigned_for")

@admin.register(UserPosition)
class UserPositionAdmin(admin.ModelAdmin):
    list_display = ("user","position","approved_by",)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)