from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from kresh_energy_be.users.tests.factories import UserFactory

from ..models import CreditEntryType
from ..models import ReferralCredit
from .factories import ReferralFactory
from .factories import set_reward_settings

pytestmark = pytest.mark.django_db


class TestReferralCodeCheckView:
    def test_valid_code_for_anonymous_caller(self):
        referrer = UserFactory.create()
        client = APIClient()
        response = client.post(
            "/api/referrals/check-code/",
            {"code": referrer.referral_code},
        )
        assert response.status_code == 200
        assert response.data == {"valid": True}

    def test_unknown_code_is_invalid(self):
        client = APIClient()
        response = client.post("/api/referrals/check-code/", {"code": "NOSUCHCODE"})
        assert response.status_code == 200
        assert response.data == {"valid": False}

    def test_own_code_is_invalid_for_self_referral(self):
        user = UserFactory.create()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/referrals/check-code/", {"code": user.referral_code})
        assert response.status_code == 200
        assert response.data == {"valid": False}


class TestMyReferralDashboardView:
    def test_requires_authentication(self):
        client = APIClient()
        response = client.get("/api/referrals/me/")
        assert response.status_code in (401, 403)

    def test_returns_dashboard_shape_for_authenticated_user(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        user = UserFactory.create()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/referrals/me/")
        assert response.status_code == 200
        assert response.data["referral_code"] == user.referral_code
        assert response.data["referral_code"] in response.data["referral_link"]
        assert Decimal(response.data["balance"]) == Decimal("0.00")
        assert Decimal(response.data["reward_amounts"]["referrer"]) == Decimal("50.00")
        assert response.data["referrals"] == []
        assert response.data["referred_pending"] is False

    def test_referred_pending_true_before_reward_granted(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)

        client = APIClient()
        client.force_authenticate(user=referred)
        response = client.get("/api/referrals/me/")
        assert response.data["referred_pending"] is True

    def test_referred_pending_false_once_reward_granted(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(
            referred_by=referrer,
            referral_reward_granted=True,
        )
        ReferralFactory.create(referrer=referrer, referred_user=referred)

        client = APIClient()
        client.force_authenticate(user=referred)
        response = client.get("/api/referrals/me/")
        assert response.data["referred_pending"] is False

    def test_referred_pending_false_when_program_inactive(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"), is_active=False)
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)

        client = APIClient()
        client.force_authenticate(user=referred)
        response = client.get("/api/referrals/me/")
        assert response.data["referred_pending"] is False


class TestRedemptionRequestViewSet:
    def test_rejects_when_balance_is_zero(self):
        user = UserFactory.create()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/referrals/redemptions/", {})
        assert response.status_code == 400

    def test_creates_pending_request_when_balance_available(self):
        user = UserFactory.create()
        ReferralCredit.objects.create(
            user=user,
            entry_type=CreditEntryType.EARNED_AS_REFERRER,
            amount=Decimal("50.00"),
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/referrals/redemptions/", {})
        assert response.status_code == 201
        assert Decimal(response.data["amount_requested"]) == Decimal("50.00")

    def test_requires_authentication(self):
        client = APIClient()
        response = client.post("/api/referrals/redemptions/", {})
        assert response.status_code in (401, 403)
