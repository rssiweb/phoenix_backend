from rest_framework import serializers
from api.models import (
    Branch,
    Session,
    Subject,
    Category,
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
        fields = ["name", "timezone"]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ["name"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ["name"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["name"]


class GradeSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeSystem
        fields = ["name"]


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["name"]


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["name"]


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ["name"]


class ClassAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassAttendance
        fields = ["name"]


class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = ["name"]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["name"]


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ["name"]


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ["name"]
