from email.headerregistry import Group
from functools import partial
from rest_framework import viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from api.constants import USER_TYPE_ADMIN, USER_TYPE_FACULTY, USER_TYPE_STUDENT
from api.filters import (
    StudentInClassroomFilterBackend,
    ClassOccurrenceFilterSet,
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
    ClassOccurrence,
    StudentAttendance,
    Exam,
    Test,
    Mark,
    User,
)
from api.models.core import BranchSessionAssociation
from api.serializers import (
    AttendanceByStudentSerializer,
    BranchSerializer,
    BranchSessionAssociationSerializer,
    CreateClassOccurranceSerializer,
    CreateStudentAttendanceSerializer,
    SessionSerializer,
    SubjectSerializer,
    CategorySerializer,
    FacultySerializer,
    StudentSerializer,
    GradeSystemSerializer,
    GradeSerializer,
    ClassroomSerializer,
    LeaveSerializer,
    ClassOccurranceSerializer,
    StudentAttendanceSerializer,
    ExamSerializer,
    TestSerializer,
    MarkSerializer,
    UpdateStudentAttendanceSerializer,
    UserSerializer,
)


class AuthTokenView(ObtainAuthToken):
    "Auth view expects username and password as POST payload"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
                "type": user.type,
            }
        )


class AuthenticatedMixin:
    permission_classes = (IsAuthenticated,)


class BSAViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):

    queryset = BranchSessionAssociation.objects.all()
    serializer_class = BranchSessionAssociationSerializer
    filterset_fields = [
        "branch",
    ]

    @action(detail=False)
    def branches(self, request):
        items = self.get_queryset()

        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


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


class UserViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Faculty view
    """

    lookup_field = "username"
    queryset = User.objects.all()

    @action(detail=False, methods=["get"])
    def me(self, request):
        user = request.user
        serializer_class, attr = {
            USER_TYPE_FACULTY: (FacultySerializer, "faculty"),
            USER_TYPE_STUDENT: (StudentSerializer, "student"),
            USER_TYPE_ADMIN: (UserSerializer, None),
        }[user.type]
        serializer = serializer_class(getattr(user, attr) if attr else user)
        return Response(serializer.data)

    def get_object(self):
        user = super().get_object()
        if user.type == USER_TYPE_FACULTY:
            return user.faculty
        elif user.type == USER_TYPE_STUDENT:
            return user.student
        return user

    def get_serializer_class(self):
        if self.action in ("list",):
            return UserSerializer
        else:
            if self.request.user.type == USER_TYPE_FACULTY:
                return FacultySerializer
            elif self.request.user.type == USER_TYPE_STUDENT:
                return StudentSerializer
            return UserSerializer


class FacultyViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Faculty view
    """

    lookup_field = "profile__user__username"
    queryset = Faculty.objects
    serializer_class = FacultySerializer
    filterset_fields = ["branch__name", "profile__gender"]


class StudentViewSet(AuthenticatedMixin, viewsets.ReadOnlyModelViewSet):
    """
    Student view
    """

    lookup_field = "profile__user__username"
    queryset = Student.objects
    serializer_class = StudentSerializer


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

    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    filterset_fields = ["subject", "faculty__user", "bsa__branch", "bsa__session"]

    @action(detail=True, methods=["get"])
    def students(self, request, pk):
        classroom = self.get_object()
        students = classroom.students.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def attendance(self, request, pk):
        classroom = self.get_object()
        occurrences = classroom.classoccurrence_set.all()
        serializer = ClassOccurranceSerializer(occurrences, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def attendance_by_student(self, request, pk):
        classroom = self.get_object()
        students = classroom.students.all()
        for student in students:
            student.attendance = StudentAttendance.objects.filter(
                class_occurrance__classroom=classroom, student=student
            ).all()
        serializer = AttendanceByStudentSerializer(
            students, many=True, context={"classroom": classroom}
        )
        return Response(serializer.data)


class LeaveViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    Leave view
    """

    queryset = Leave.objects
    serializer_class = LeaveSerializer
    filterset_fields = ["student__profile__profile_id", "from_date", "to_date"]


class ClassOccurranceViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    ClassOccurrance view
    """

    queryset = ClassOccurrence.objects
    filterset_class = ClassOccurrenceFilterSet

    def get_serializer_class(self):
        if self.action in ("create",):
            return CreateClassOccurranceSerializer
        return ClassOccurranceSerializer


class StudentAttendanceViewSet(AuthenticatedMixin, viewsets.ModelViewSet):
    """
    StudentAttendance view
    """

    queryset = StudentAttendance.objects
    serializer_class = StudentAttendanceSerializer
    filterset_class = StudentAttendanceFilterSet
    # should be faculty in class or part of admin group

    # filterset_fields = ["class_attendance", "student__profile__profile_id"]

    def get_serializer_class(self):
        if self.action in ("create",):
            return CreateStudentAttendanceSerializer
        elif self.action in ("partial_update",):
            return UpdateStudentAttendanceSerializer
        return StudentAttendanceSerializer


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
    filterset_fields = ["test"]
