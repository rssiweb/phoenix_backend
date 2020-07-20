from rest_framework import viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.filters import (
    StudentInClassroomFilterBackend,
    ClassAttendanceFilterSet,
    StudentAttendanceFilterSet,
)
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


class BranchViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Branch view
    """

    queryset = Branch.objects
    serializer_class = BranchSerializer
    filterset_fields = [
        "name",
    ]


class SessionViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Session view
    """

    queryset = Session.objects
    serializer_class = SessionSerializer
    filterset_fields = [
        "name",
    ]


class SubjectViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Session view
    """

    queryset = Subject.objects
    serializer_class = SubjectSerializer
    filterset_fields = ["name", "session__name"]


class CategoryViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Category view
    """

    queryset = Category.objects
    serializer_class = CategorySerializer
    filterset_fields = ["name", "session__name"]


class FacultyViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Faculty view
    """

    queryset = Faculty.objects
    serializer_class = FacultySerializer
    filterset_fields = ["profile__profile_id", "branch__name", "profile__gender"]


class StudentViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Student view
    """

    queryset = Student.objects
    serializer_class = StudentSerializer
    filterset_fields = ["profile__profile_id", "session__name", "category__name"]


class StudentsInClassViewSet(
    AuthenticatedMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Students in Class view
    """

    queryset = Student.objects
    serializer_class = StudentSerializer
    filter_backends = [StudentInClassroomFilterBackend]
    filterset_fields = ["classroom"]


class GradeSystemViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    GradeSystem view
    """

    queryset = GradeSystem.objects
    serializer_class = GradeSystemSerializer
    filterset_fields = ["session__name", "name"]


class GradeViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Grade view
    """

    queryset = Grade.objects
    serializer_class = GradeSerializer
    filterset_fields = ["grade_system__name"]


class ClassroomViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Classroom view
    """

    queryset = Classroom.objects
    serializer_class = ClassroomSerializer
    filterset_fields = [
        "session__name",
        "categories",
        "faculty__profile__profile_id",
        "subject__name",
    ]


class LeaveViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Leave view
    """

    queryset = Leave.objects
    serializer_class = LeaveSerializer
    filterset_fields = ["student__profile__profile_id", "from_date", "to_date"]


class ClassAttendanceViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    ClassAttendance view
    """

    queryset = ClassAttendance.objects
    serializer_class = ClassAttendanceSerializer
    filterset_class = ClassAttendanceFilterSet


class StudentAttendanceViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    StudentAttendance view
    """

    queryset = StudentAttendance.objects
    serializer_class = StudentAttendanceSerializer
    filterset_class = StudentAttendanceFilterSet
    # filterset_fields = ["class_attendance", "student__profile__profile_id"]


class ExamViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Exam view
    """

    queryset = Exam.objects
    serializer_class = ExamSerializer
    filterset_fields = ["session__name", "name"]


class TestViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Test view
    """

    queryset = Test.objects
    serializer_class = TestSerializer
    filterset_fields = ["exam", "classroom__name", "name", "evaluator", "date"]


class MarkViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Mark view
    """

    queryset = Mark.objects
    serializer_class = MarkSerializer
    filterset_fields = ["test", "student__profile__profile_id"]
