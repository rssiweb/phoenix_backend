from rest_framework import viewsets
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
from api.serializers import (
    BranchSerializer,
    SessionSerializer,
    SubjectSerializer,
    CategorySerializer,
    FacultySerializer,
    StudentSerializer,
    GradeSystemSerializer,
    GradeSerializer,
    ClassroomSerializer,
    LeaveSerializer,
    ClassAttendanceSerializer,
    StudentAttendanceSerializer,
    ExamSerializer,
    TestSerializer,
    MarkSerializer,
)


class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Branch view
    """

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Session view
    """

    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Session view
    """

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category view
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Faculty view
    """

    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Student view
    """

    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class GradeSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GradeSystem view
    """

    queryset = GradeSystem.objects.all()
    serializer_class = GradeSystemSerializer


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Grade view
    """

    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class ClassroomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Classroom view
    """

    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class LeaveViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Leave view
    """

    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer


class ClassAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ClassAttendance view
    """

    queryset = ClassAttendance.objects.all()
    serializer_class = ClassAttendanceSerializer


class StudentAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    StudentAttendance view
    """

    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exam view
    """

    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


class TestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Test view
    """

    queryset = Test.objects.all()
    serializer_class = TestSerializer


class MarkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Mark view
    """

    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
