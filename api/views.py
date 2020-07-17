from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

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


class AuthTokenView(ObtainAuthToken):
    "Auth view expects username and password as POST payload"

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


class AuthenticatedMixin:
    permission_classes = (IsAuthenticated,)


class BranchViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Branch view
    """

    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filterset_fields = [
        "name",
    ]


class SessionViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Session view
    """

    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filterset_fields = [
        "name",
    ]


class SubjectViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Session view
    """

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filterset_fields = ["name", "session__name"]


class CategoryViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Category view
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["name", "session__name"]


class FacultyViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Faculty view
    """

    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    filterset_fields = ["profile__profile_id", "branch__name", "profile__gender"]


class StudentViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Student view
    """

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filterset_fields = ["profile__profile_id", "session__name", "category__name"]


class IsStudentInClassroomFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        classroom_id = self.request.query_params.get("classroom", None)
        classroom = get_object_or_404(Classroom, pk=int(classroom_id))
        return queryset.filter(category__in=classroom.categories,)


class StudentsInClassView(AuthenticatedMixin, generics.ListAPIView):
    """
    Students in Class view
    """

    queryset = Student.objects
    serializer_class = StudentSerializer
    # filterset_fields = ["classroom"]

    # def filter_queryset(self, queryset):
    #     filtered_queryset = super().filter_queryset(queryset)
    #     # classroom_id = self.request.query_params.get("classroom", None)
    #     # classroom = get_object_or_404(Classroom, pk=int(classroom_id))
    #     # print(classroom.categories.all())
    #     return filtered_queryset
    def list(self, request, *args, **kwargs):
        return Student.objects.all()


class GradeSystemViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    GradeSystem view
    """

    queryset = GradeSystem.objects.all()
    serializer_class = GradeSystemSerializer
    filterset_fields = ["session__name", "name"]


class GradeViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Grade view
    """

    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filterset_fields = ["grade_system__name"]


class ClassroomViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Classroom view
    """

    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    filterset_fields = [
        "session__name",
        "categories",
        "faculty__profile__profile_id",
        "subject__name",
    ]


class LeaveViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Leave view
    """

    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    filterset_fields = ["student__profile__profile_id", "from_date", "to_date"]


class ClassAttendanceViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    ClassAttendance view
    """

    queryset = ClassAttendance.objects.all()
    serializer_class = ClassAttendanceSerializer
    filterset_fields = ["classroom__name", "faculty__profile__profile_id"]


class StudentAttendanceViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    StudentAttendance view
    """

    queryset = StudentAttendance.objects.all()
    serializer_class = StudentAttendanceSerializer
    filterset_fields = ["class_attendance", "student__profile__profile_id"]


class ExamViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Exam view
    """

    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    filterset_fields = ["session__name", "name"]


class TestViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Test view
    """

    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filterset_fields = ["exam", "classroom__name", "name", "evaluator", "date"]


class MarkViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Mark view
    """

    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    filterset_fields = ["test", "student__profile__profile_id"]
