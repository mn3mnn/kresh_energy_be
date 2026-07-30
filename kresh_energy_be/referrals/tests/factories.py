from __future__ import annotations

from decimal import Decimal

from factory import SubFactory
from factory.django import DjangoModelFactory

from kresh_energy_be.users.tests.factories import UserFactory

from ..models import Referral
from ..models import ReferralDiscount
from ..models import ReferralDiscountStatus
from ..models import ReferralStatus


def set_reward_settings(
    referrer_amount: Decimal = Decimal("50.00"),
    referred_amount: Decimal = Decimal("25.00"),
    *,
    is_active: bool = True,
):
    """Configure the singleton reward-amount row for a test.

    Not a factory: ReferralRewardSettings.save() forces pk=1, which doesn't
    play well with factory-boy's default `objects.create()` (force_insert).
    """
    from ..models import ReferralRewardSettings

    settings_row = ReferralRewardSettings.get_instance()
    settings_row.referrer_reward_amount = referrer_amount
    settings_row.referred_reward_amount = referred_amount
    settings_row.is_active = is_active
    settings_row.save()
    return settings_row


class ReferralFactory(DjangoModelFactory):
    referrer = SubFactory(UserFactory)
    referred_user = SubFactory(UserFactory)
    code_used = "TESTCODE"
    status = ReferralStatus.SIGNED_UP

    class Meta:
        model = Referral


class ReferralDiscountFactory(DjangoModelFactory):
    owner = SubFactory(UserFactory)
    referral = SubFactory(ReferralFactory)
    amount = Decimal("50.00")
    status = ReferralDiscountStatus.AVAILABLE

    class Meta:
        model = ReferralDiscount
