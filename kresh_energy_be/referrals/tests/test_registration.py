from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from kresh_energy_be.users.models import User

pytestmark = pytest.mark.django_db


def register(client: APIClient, **overrides):
    payload = {
        "email": "newuser@example.com",
        "password1": "Xk9-mQ2vLp7-Rt4w",
        "password2": "Xk9-mQ2vLp7-Rt4w",
        "name": "Jane Doe",
    }
    payload.update(overrides)
    return client.post("/api/auth/registration/", payload)


class TestRegistrationName:
    def test_missing_name_is_rejected(self):
        client = APIClient()
        response = register(client, name="")
        assert response.status_code == 400
        assert "name" in response.data

    def test_name_not_provided_at_all_is_rejected(self):
        client = APIClient()
        payload = {
            "email": "newuser@example.com",
            "password1": "Xk9-mQ2vLp7-Rt4w",
            "password2": "Xk9-mQ2vLp7-Rt4w",
        }
        response = client.post("/api/auth/registration/", payload)
        assert response.status_code == 400
        assert "name" in response.data

    def test_valid_name_is_stored(self):
        client = APIClient()
        response = register(client, name="Jane Doe")
        assert response.status_code == 201
        user = User.objects.get(email="newuser@example.com")
        assert user.name == "Jane Doe"


class TestRegistrationPhone:
    def test_phone_is_optional(self):
        client = APIClient()
        response = register(client)
        assert response.status_code == 201
        user = User.objects.get(email="newuser@example.com")
        assert user.phone == ""

    def test_valid_international_phone_is_accepted_and_normalized(self):
        client = APIClient()
        response = register(client, phone="+49 151 23456789")
        assert response.status_code == 201
        user = User.objects.get(email="newuser@example.com")
        assert str(user.phone) == "+4915123456789"

    def test_valid_phone_from_another_country_is_accepted(self):
        client = APIClient()
        response = register(client, phone="+1 (415) 555-2671")
        assert response.status_code == 201
        user = User.objects.get(email="newuser@example.com")
        assert str(user.phone) == "+14155552671"

    def test_missing_country_code_is_rejected(self):
        client = APIClient()
        response = register(client, phone="0151 23456789")
        assert response.status_code == 400
        assert "phone" in response.data

    def test_garbage_phone_is_rejected(self):
        client = APIClient()
        response = register(client, phone="not-a-phone-number")
        assert response.status_code == 400
        assert "phone" in response.data
