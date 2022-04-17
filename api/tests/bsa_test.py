from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase



class BsaTest(APITestCase):
    fixtures = [
        "fixtures/test.json",
    ]

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username="admin", password="zkhan1993")

    def test_read_bsa(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse("branchsessionassociation-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)