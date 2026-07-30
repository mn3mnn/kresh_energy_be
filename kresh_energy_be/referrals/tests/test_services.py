from __future__ import annotations

from decimal import Decimal

import pytest

from kresh_energy_be.leads.models import InspectionBooking
from kresh_energy_be.leads.models import QuoteRequest
from kresh_energy_be.users.tests.factories import UserFactory

from ..models import Referral
from ..models import ReferralDiscount
from ..models import ReferralDiscountStatus
from ..models import ReferralStatus
from ..services import credit_referral_reward
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


def make_booking(submitted_by=None, **kwargs) -> InspectionBooking:
    defaults = {
        "full_name": "Test Submitter",
        "phone": "+49 123",
        "email": "submitter@example.com",
        "address": "Somewhere 1, Berlin",
        "preferred_date": "2026-08-01",
    }
    defaults.update(kwargs)
    return InspectionBooking.objects.create(submitted_by=submitted_by, **defaults)


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

        referrer_discount = ReferralDiscount.objects.get(owner=referrer, referral=referral)
        assert referrer_discount.amount == Decimal("50.00")
        assert referrer_discount.status == ReferralDiscountStatus.AVAILABLE
        assert referrer_discount.quote_request_id is None

        referred_discount = ReferralDiscount.objects.get(owner=referred, referral=referral)
        assert referred_discount.amount == Decimal("25.00")
        assert referred_discount.status == ReferralDiscountStatus.APPLIED
        assert referred_discount.quote_request_id == quote.pk
        assert referred_discount.applied_at is not None

    def test_referred_persons_voucher_is_available_when_qualified_by_booking(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        referral = ReferralFactory.create(referrer=referrer, referred_user=referred)

        booking = make_booking(submitted_by=referred)
        credit_referral_reward(booking)

        referred_discount = ReferralDiscount.objects.get(owner=referred, referral=referral)
        assert referred_discount.status == ReferralDiscountStatus.AVAILABLE
        assert referred_discount.quote_request_id is None

    def test_noop_for_anonymous_submission(self):
        set_reward_settings()
        quote = make_quote(submitted_by=None)
        credit_referral_reward(quote)  # must not raise
        assert ReferralDiscount.objects.count() == 0

    def test_noop_when_user_has_no_referrer(self):
        set_reward_settings()
        user = UserFactory.create()
        quote = make_quote(submitted_by=user)
        credit_referral_reward(quote)
        assert ReferralDiscount.objects.count() == 0

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
        assert ReferralDiscount.objects.count() == 0

    def test_noop_when_program_inactive(self):
        set_reward_settings(is_active=False)
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)
        quote = make_quote(submitted_by=referred)
        credit_referral_reward(quote)
        assert ReferralDiscount.objects.count() == 0

    def test_second_qualifying_lead_does_not_double_credit(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred)

        credit_referral_reward(make_quote(submitted_by=referred))
        credit_referral_reward(make_quote(submitted_by=referred))

        assert ReferralDiscount.objects.filter(owner=referrer).count() == 1

    def test_two_qualifying_referrals_produce_two_separate_vouchers(self):
        set_reward_settings(Decimal("50.00"), Decimal("25.00"))
        referrer = UserFactory.create()
        referred_one = UserFactory.create(referred_by=referrer)
        referred_two = UserFactory.create(referred_by=referrer)
        ReferralFactory.create(referrer=referrer, referred_user=referred_one)
        ReferralFactory.create(referrer=referrer, referred_user=referred_two)

        credit_referral_reward(make_quote(submitted_by=referred_one))
        credit_referral_reward(make_quote(submitted_by=referred_two))

        vouchers = ReferralDiscount.objects.filter(
            owner=referrer,
            status=ReferralDiscountStatus.AVAILABLE,
        )
        assert vouchers.count() == 2

    def test_referral_row_survives_when_a_discount_is_deleted(self):
        # Referral.discounts uses on_delete=CASCADE on ReferralDiscount, not
        # the other way around — deleting a voucher must not touch Referral.
        set_reward_settings()
        referrer = UserFactory.create()
        referred = UserFactory.create(referred_by=referrer)
        referral = ReferralFactory.create(referrer=referrer, referred_user=referred)
        credit_referral_reward(make_quote(submitted_by=referred))

        ReferralDiscount.objects.filter(owner=referrer).delete()
        assert Referral.objects.filter(pk=referral.pk).exists()
