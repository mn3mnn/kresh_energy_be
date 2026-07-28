from __future__ import annotations

from decimal import Decimal

import pytest

from kresh_energy_be.leads.models import QuoteRequest
from kresh_energy_be.users.tests.factories import UserFactory

from ..models import CreditEntryType
from ..models import Referral
from ..models import ReferralCredit
from ..models import ReferralStatus
from ..services import credit_referral_reward
from ..services import get_balance
from ..services import request_redemption
from .factories import ReferralFactory
from .factories import set_reward_settings

pytestmark = pytest.mark.django_db


def make_quote(submitted_by=None, **kwargs) -> QuoteRequest:
    defaults = {
        "full_name": "Test Submitter",
        "phone": "+49 123",
        "email": "submitter@example.com",
        "address": "Somewhere 1, Berlin",
    }
    defaults.update(kwargs)
    return QuoteRequest.objects.create(submitted_by=submitted_by, **defaults)


class TestGetBalance:
    def test_zero_for_user_with_no_credits(self):
        user = UserFactory.create()
        assert get_balance(user) == Decimal("0")

    def test_sums_earned_minus_redeemed(self):
        user = UserFactory.create()
        ReferralCredit.objects.create(
            user=user,
            entry_type=CreditEntryType.EARNED_AS_REFERRER,
            amount=Decimal("50.00"),
        )
        ReferralCredit.objects.create(
            user=user,
            entry_type=CreditEntryType.REDEEMED,
            amount=Decimal("20.00"),
        )
        assert get_balance(user) == Decimal("30.00")


class TestCreditReferralReward:
    def test_happy_path_credits_both_sides_once(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        referral = ReferralFactory.create(referrer=referrer, referred_user=referred)

        quote = make_quote(submitted_by=referred)
        credit_referral_reward(quote)

        referral.refresh_from_db()
        referred.refresh_from_db()
        assert referral.status == ReferralStatus.REWARDED
        assert referral.qualifying_quote_id == quote.pk
        assert referred.referral_reward_granted is True
        assert get_balance(referrer) == Decimal("50.00")
        # Referred person's own reward is earned and auto-redeemed in the
        # same transaction against their triggering quote, so nets to 0.
        assert get_balance(referred) == Decimal("0.00")

    def test_noop_for_anonymous_submission(self):
        set_reward_settings()
        quote = make_quote(submitted_by=None)
        credit_referral_reward(quote)  # must not raise
        assert ReferralCredit.objects.count() == 0

    def test_noop_when_user_has_no_referrer(self):
        set_reward_settings()
        user = UserFactory.create()
        quote = make_quote(submitted_by=user)
        credit_referral_reward(quote)
        assert ReferralCredit.objects.count() == 0

    def test_noop_when_already_granted(self):
        set_reward_settings()
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer, referral_reward_granted=True)
        ReferralFactory.create(
            referrer=referrer,
            referred_user=referred,
            status=ReferralStatus.REWARDED,
        )
        quote = make_quote(submitted_by=referred)
        credit_referral_reward(quote)
        assert ReferralCredit.objects.count() == 0

    def test_noop_when_program_inactive(self):
        set_reward_settings(is_active=False)
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)
        quote = make_quote(submitted_by=referred)
        credit_referral_reward(quote)
        assert ReferralCredit.objects.count() == 0

    def test_second_qualifying_lead_does_not_double_credit(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)

        credit_referral_reward(make_quote(submitted_by=referred))
        credit_referral_reward(make_quote(submitted_by=referred))

        assert get_balance(referrer) == Decimal("50.00")
        assert Referral.objects.filter(referred_user=referred).count() == 1


class TestRequestRedemption:
    def test_returns_none_when_balance_is_zero(self):
        user = UserFactory.create()
        assert request_redemption(user) is None

    def test_creates_pending_request_for_full_balance(self):
        user = UserFactory.create()
        ReferralCredit.objects.create(
            user=user,
            entry_type=CreditEntryType.EARNED_AS_REFERRER,
            amount=Decimal("50.00"),
        )
        redemption = request_redemption(user)
        assert redemption is not None
        assert redemption.amount_requested == Decimal("50.00")
        assert redemption.status == "pending"
