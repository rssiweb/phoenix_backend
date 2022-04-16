import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Classroom
from api.models.attendance import StudentAttendance
from api.models.core import ClassroomManager

from api.urls import router
from pprint import pprint

pprint(router.urls)


class AccountTests(APITestCase):
    fixtures = [
        "fixtures/test.json",
    ]

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username="admin", password="zkhan1993")

    def test_read_classoccurrence(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("classoccurrence-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_create_attendance(self):
        """
        Ensure we can create a new attendance object.
        """
        url = reverse("studentattendance-list")
        response = self.client.post(
            url,
            dict(
                faculty="admin",
                student="VLK0001",
                class_occurrance=1,
                attendance="P",
                comment="",
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_attendance(self):
        """
        Ensure we can create a new attendance object.
        """
        data = dict(
            faculty="admin",
            student="VLK0001",
            class_occurrance=1,
            attendance="P",
            comment="",
        )
        url = reverse("studentattendance-list")
        response = self.client.post(url, data, format="json",)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse("studentattendance-detail", args=(2,))
        data["attendance"] = "A"
        response = self.client.patch(url, data, format="json",)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attendance_id = response.data["id"]
        self.assertEqual(
            StudentAttendance.objects.get(pk=attendance_id).attendance, "A"
        )
