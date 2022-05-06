from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import User


class UserTest(APITestCase):
    fixtures = [
        "fixtures/core.json",
        "fixtures/user.json",
    ]

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username="admin", password="zkhan1993")

    def test_read_users(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("user-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
