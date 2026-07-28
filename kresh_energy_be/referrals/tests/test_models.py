from __future__ import annotations

import pytest
from django.db import IntegrityError
from django.db import transaction

from kresh_energy_be.users.tests.factories import UserFactory

from ..models import Referral
from ..models import ReferralRewardSettings
from .factories import ReferralFactory

pytestmark = pytest.mark.django_db


class TestReferralRewardSettings:
    def test_get_instance_is_singleton(self):
        first = ReferralRewardSettings.get_instance()
        second = ReferralRewardSettings.get_instance()
        assert first.pk == second.pk == 1
        assert ReferralRewardSettings.objects.count() == 1

    def test_save_always_forces_pk_1(self):
        row = ReferralRewardSettings.get_instance()
        row.is_active = False
        row.save()
        assert ReferralRewardSettings.objects.count() == 1
        assert ReferralRewardSettings.objects.get().pk == 1

    def test_delete_is_a_no_op(self):
        row = ReferralRewardSettings.get_instance()
        row.delete()
        assert ReferralRewardSettings.objects.count() == 1


class TestReferral:
    def test_one_referral_per_referred_user(self):
        referred = UserFactory.create()
        ReferralFactory.create(referred_user=referred)
        with pytest.raises(IntegrityError), transaction.atomic():
            ReferralFactory.create(referred_user=referred)
        assert Referral.objects.filter(referred_user=referred).count() == 1


class TestUserReferralCode:
    def test_referral_code_auto_generated_on_save(self):
        user = UserFactory.create()
        assert user.referral_code
        assert len(user.referral_code) == 8

    def test_referral_code_not_overwritten_on_resave(self):
        user = UserFactory.create()
        original_code = user.referral_code
        user.name = "Changed"
        user.save()
        user.refresh_from_db()
        assert user.referral_code == original_code
