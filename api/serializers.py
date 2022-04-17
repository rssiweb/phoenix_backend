from rest_framework import serializers
from django.contrib.auth.models import User, Group
from api.models import (
    Branch,
    Session,
    Subject,
    Category,
    User,
    Faculty,
    Student,
    GradeSystem,
    Grade,
    Classroom,
    Leave,
    ClassOccurrence,
    StudentAttendance,
    Exam,
    Test,
    Mark,
)
from api.models.core import BranchSessionAssociation
from api.models.user import USER_TYPE_CHOICES
from django.utils import timezone


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("__all__",)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    full_name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = (
            "password",
            "user_permissions",
            "is_superuser",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
        )

    def get_full_name(self, model):
        return model.get_full_name()

    def get_type(self, model):
        return dict(USER_TYPE_CHOICES)[model.type]


class FacultySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Faculty
        fields = "__all__"

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.update(res.pop("user"))
        return res


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = "__all__"

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.update(res.pop("user"))
        return res


class GradeSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeSystem
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = "__all__"


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"


class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = "__all__"


class CreateStudentAttendanceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    date = serializers.DateTimeField(
        source="class_occurrance.start_time", read_only=True
    )
    faculty = serializers.CharField()
    student = serializers.CharField()

    class Meta:
        model = StudentAttendance
        fields = [
            "date",
            "faculty",
            "student",
            "class_occurrance",
            "comment",
            "attendance",
            "id",
        ]

    def validate_faculty(self, username):
        try:
            return Faculty.objects.get(user__username=username)
        except Faculty.DoesNotExist:
            raise serializers.ValidationError("Invalid faculty value")

    def validate_student(self, username):
        try:
            return Student.objects.get(user__username=username)
        except Faculty.DoesNotExist:
            raise serializers.ValidationError("Invalid value")


class UpdateStudentAttendanceSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="class_occurrance.start_time")

    class Meta:
        model = StudentAttendance
        fields = ["comment", "attendance", "id", "date"]


class ClassOccurranceSerializer(serializers.ModelSerializer):
    faculty = serializers.CharField(source="faculty.user.username")

    class Meta:
        model = ClassOccurrence
        fields = "__all__"


class CreateClassOccurranceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    faculty = serializers.CharField()
    start_time = serializers.DateTimeField(
        default_timezone=timezone.get_current_timezone()
    )

    class Meta:
        model = ClassOccurrence
        fields = ["id", "start_time", "classroom", "faculty"]

    def validate_faculty(self, username):
        try:
            return Faculty.objects.get(user__username=username)
        except Faculty.DoesNotExist:
            raise serializers.ValidationError("Invalid faculty value")


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = "__all__"


class BranchSessionAssociationSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    session = SessionSerializer()

    class Meta:
        model = BranchSessionAssociation
        fields = "__all__"


class AttendanceByStudentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    attendance = UpdateStudentAttendanceSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ["category", "attendance", "id", "name"]

    def get_name(self, model):
        return model.user.get_full_name()

    def get_id(self, model):
        return model.user.username

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["attendance"] = sorted(data.pop("attendance", []), key=lambda x: x["date"])
        return data
