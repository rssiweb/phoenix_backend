from rest_framework import serializers
from django.contrib.auth.models import User
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
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class FacultySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profile_id = serializers.CharField(source="profile.profile_id")
    profile_pic = serializers.CharField(source="profile.profile_pic")
    gender = serializers.CharField(source="profile.gender")
    dob = serializers.DateField(source="profile.dob")
    inactive_from = serializers.DateTimeField(source="profile.inactive_from")

    def get_name(self, obj):
        return obj.profile.user.get_full_name()

    class Meta:
        model = Faculty
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profile_id = serializers.CharField(source="profile.profile_id")
    profile_pic = serializers.CharField(source="profile.profile_pic")
    gender = serializers.CharField(source="profile.gender")
    dob = serializers.DateField(source="profile.dob")
    inactive_from = serializers.DateTimeField(source="profile.inactive_from")

    def get_name(self, obj):
        return obj.profile.user.get_full_name()

    class Meta:
        model = Student
        fields = "__all__"


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


class StudentMinimalAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = ["id", "attendance", "comment", "student"]


class ClassAttendanceSerializer(serializers.ModelSerializer):
    entries = StudentMinimalAttendanceSerializer(
        source="studentattendance_set", many=True
    )

    class Meta:
        model = ClassAttendance
        fields = "__all__"


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
