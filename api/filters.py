from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from rest_framework.compat import coreapi, coreschema
from rest_framework import filters
from django_filters import rest_framework as dfilters
from api.models import Classroom, ClassOccurrence, StudentAttendance


class StudentInClassroomFilterBackend(filters.BaseFilterBackend):
    """
    filter the students present in a classroom
    """

    filter_param = "classroom"
    filter_title = "Classroom ID"
    filter_description = "Classroom in which students you are looking for"

    def get_schema_fields(self, view):
        assert (
            coreapi is not None
        ), "coreapi must be installed to use `get_schema_fields()`"
        assert (
            coreschema is not None
        ), "coreschema must be installed to use `get_schema_fields()`"
        return [
            coreapi.Field(
                name=self.filter_param,
                required=False,
                location="query",
                schema=coreschema.String(
                    title=force_str(self.filter_title),
                    description=force_str(self.filter_description),
                ),
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": self.filter_param,
                "required": True,
                "in": "query",
                "description": force_str(self.filter_description),
                "schema": {"type": "int"},
            },
        ]

    def filter_queryset(self, request, queryset, view):
        classroom_id = request.query_params.get("classroom", None)
        if classroom_id:
            classroom = get_object_or_404(Classroom, pk=int(classroom_id))
            return queryset.filter(category__in=classroom.categories.all(),)
        return queryset.filter(category=None)


class ClassOccurrenceFilterSet(dfilters.FilterSet):
    faculty = dfilters.CharFilter(field_name="faculty__user__username")
    start_time = dfilters.IsoDateTimeFromToRangeFilter(field_name="start_time")
    not_ended = dfilters.BooleanFilter(field_name="end_time", lookup_expr="isnull")

    class Meta:
        model = ClassOccurrence
        fields = ["classroom", "faculty", "start_time", "not_ended"]


class StudentAttendanceFilterSet(dfilters.FilterSet):
    class_attendance = dfilters.BaseInFilter(
        field_name="class_attendance", lookup_expr="in"
    )

    class Meta:
        model = StudentAttendance
        fields = ["class_attendance"]
