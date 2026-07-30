from django.db import transaction
from django.utils import timezone

from kresh_energy_be.leads.models import InspectionBooking
from kresh_energy_be.leads.models import QuoteRequest

from .emails import send_referral_reward_email
from .emails import send_referred_discount_applied_email
from .models import Referral
from .models import ReferralDiscount
from .models import ReferralDiscountStatus
from .models import ReferralRewardSettings
from .models import ReferralStatus


def credit_referral_reward(lead_instance: QuoteRequest | InspectionBooking) -> None:
    """Grant both sides of a referral the first time the referred person
    submits a qualifying quote or booking. No-ops silently for anonymous,
    non-referred, or already-rewarded users — this is called unconditionally
    from perform_create() on every lead submission.

    Creates one ReferralDiscount voucher for the referrer (AVAILABLE, to be
    picked later on a future quote) and one for the referred person. The
    referred person's voucher is auto-applied immediately if the qualifying
    event is a QuoteRequest (mirrors today's "auto-applied" welcome
    discount); if it's an InspectionBooking (no price to attach to), it's
    left AVAILABLE so it becomes a normal usable voucher on whatever quote
    the referred person submits next.
    """
    user = lead_instance.submitted_by
    if user is None or not user.referred_by_id or user.referral_reward_granted:
        return

    try:
        referral = Referral.objects.select_related("referrer").get(referred_user=user)
    except Referral.DoesNotExist:
        return
    if referral.status == ReferralStatus.REWARDED:
        return

    settings_row = ReferralRewardSettings.get_instance()
    if not settings_row.is_active:
        return

    is_quote = isinstance(lead_instance, QuoteRequest)

    with transaction.atomic():
        ReferralDiscount.objects.create(
            owner=referral.referrer,
            referral=referral,
            amount=settings_row.referrer_reward_amount,
            status=ReferralDiscountStatus.AVAILABLE,
        )
        ReferralDiscount.objects.create(
            owner=user,
            referral=referral,
            amount=settings_row.referred_reward_amount,
            status=ReferralDiscountStatus.APPLIED if is_quote else ReferralDiscountStatus.AVAILABLE,
            quote_request=lead_instance if is_quote else None,
            applied_at=timezone.now() if is_quote else None,
        )

        referral.status = ReferralStatus.REWARDED
        referral.rewarded_at = timezone.now()
        if is_quote:
            referral.qualifying_quote = lead_instance
        else:
            referral.qualifying_booking = lead_instance
        referral.save(
            update_fields=["status", "rewarded_at", "qualifying_quote", "qualifying_booking"],
        )

        user.referral_reward_granted = True
        user.save(update_fields=["referral_reward_granted"])

    send_referral_reward_email(
        referral.referrer,
        settings_row.referrer_reward_amount,
        locale=lead_instance.locale,
    )
    send_referred_discount_applied_email(
        user,
        settings_row.referred_reward_amount,
        locale=lead_instance.locale,
    )
