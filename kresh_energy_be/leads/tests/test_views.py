from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from kresh_energy_be.referrals.models import Referral
from kresh_energy_be.referrals.models import ReferralStatus
from kresh_energy_be.referrals.tests.factories import ReferralFactory
from kresh_energy_be.referrals.tests.factories import set_reward_settings
from kresh_energy_be.users.tests.factories import UserFactory

from ..models import QuoteRequest

pytestmark = pytest.mark.django_db


def submit_quote(client: APIClient, **overrides):
    payload = {
        "full_name": "Jane Doe",
        "phone": "+49 123456",
        "email": "jane@example.com",
        "address": "Musterstrasse 1, Berlin",
    }
    payload.update(overrides)
    return client.post("/api/quotes/", payload)


class TestQuoteRequestReferralHook:
    def test_anonymous_non_referred_submission_is_unaffected(self):
        client = APIClient()
        response = submit_quote(client)
        assert response.status_code == 201
        quote = QuoteRequest.objects.get(pk=response.data["id"])
        assert quote.submitted_by is None

    def test_authenticated_non_referred_submission_does_not_fire_reward(self):
        set_reward_settings()
        user = UserFactory.create()
        client = APIClient()
        client.force_authenticate(user=user)
        response = submit_quote(client)
        assert response.status_code == 201
        quote = QuoteRequest.objects.get(pk=response.data["id"])
        assert quote.submitted_by == user

    def test_referred_users_first_submission_fires_reward(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)

        client = APIClient()
        client.force_authenticate(user=referred)
        response = submit_quote(client)
        assert response.status_code == 201

        referral = Referral.objects.get(referred_user=referred)
        assert referral.status == ReferralStatus.REWARDED
        referred.refresh_from_db()
        assert referred.referral_reward_granted is True
