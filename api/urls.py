from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views


router = DefaultRouter()

router.register(r"branch", views.BranchViewSet)
router.register(r"session", views.SessionViewSet)
router.register(r"subjectL", views.SubjectViewSet)
router.register(r"category", views.CategoryViewSet)
router.register(r"faculty", views.FacultyViewSet)
router.register(r"student", views.StudentViewSet)
router.register(r"grade-system", views.GradeSystemViewSet)
router.register(r"grade", views.GradeViewSet)
router.register(r"classroom", views.ClassroomViewSet)
router.register(r"leave", views.LeaveViewSet)
router.register(r"class-attendance", views.ClassAttendanceViewSet)
router.register(r"student-attendance", views.StudentAttendanceViewSet)
router.register(r"exam", views.ExamViewSet)
router.register(r"test", views.TestViewSet)
router.register(r"mark", views.MarkViewSet)

urlpatterns = [
    path("", include(router.urls)),
]