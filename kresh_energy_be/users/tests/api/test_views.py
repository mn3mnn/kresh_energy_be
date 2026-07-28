from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rest_framework.test import APIRequestFactory

from kresh_energy_be.users.api.views import UserViewSet

if TYPE_CHECKING:
    from kresh_energy_be.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    def test_me(self, user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[misc,call-arg,arg-type]

        assert response.data == {
            "username": user.username,
            "url": f"http://testserver/api/users/{user.username}/",
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "referral_code": user.referral_code,
        }
