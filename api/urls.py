from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views
from api.views import auth as auth_views

router = DefaultRouter()

router.register(r"user", views.UserViewSet)
router.register(r"bsa", views.BSAViewSet)
router.register(r"class", views.ClassroomViewSet)
router.register(r"class-occurrence", views.ClassOccurranceViewSet)
router.register(r"attendance", views.StudentAttendanceViewSet)

router.register(r"branch", views.BranchViewSet)
router.register(r"session", views.SessionViewSet)
router.register(r"subject", views.SubjectViewSet)
router.register(r"category", views.CategoryViewSet)
router.register(r"faculty", views.FacultyViewSet)
router.register(r"student", views.StudentViewSet)
router.register(r"grade-system", views.GradeSystemViewSet)
router.register(r"grade", views.GradeViewSet)
router.register(r"leave", views.LeaveViewSet)


router.register(r"exam", views.ExamViewSet)
router.register(r"test", views.TestViewSet)
router.register(r"mark", views.MarkViewSet)
router.register(r"classroom-students", views.StudentsInClassViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", auth_views.AuthTokenView.as_view()),
]
