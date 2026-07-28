from decimal import Decimal

from django.db import transaction
from django.db.models import Case
from django.db.models import DecimalField
from django.db.models import F
from django.db.models import Sum
from django.db.models import When
from django.utils import timezone

from kresh_energy_be.leads.models import InspectionBooking
from kresh_energy_be.leads.models import QuoteRequest
from kresh_energy_be.users.models import User

from .emails import send_referral_reward_email
from .models import CreditEntryType
from .models import Referral
from .models import ReferralCredit
from .models import ReferralRewardSettings
from .models import ReferralStatus
from .models import RedemptionRequest
from .models import RedemptionRequestStatus


def get_balance(user: User) -> Decimal:
    """Sum(EARNED_*) - sum(REDEEMED) for this user, from the credit ledger."""
    result = ReferralCredit.objects.filter(user=user).aggregate(
        balance=Sum(
            Case(
                When(entry_type=CreditEntryType.REDEEMED, then=-F("amount")),
                default=F("amount"),
                output_field=DecimalField(max_digits=8, decimal_places=2),
            ),
        ),
    )
    return result["balance"] or Decimal("0")


def request_redemption(
    user: User,
    quote_request: QuoteRequest | None = None,
) -> RedemptionRequest | None:
    """Create a PENDING redemption request for the user's full balance.

    Returns None (no-op) if the user has no balance to redeem. There is no
    payment system, so this is just a staff-visible annotation — see
    RedemptionRequestInline on QuoteRequestAdmin.

    Note: the balance isn't reserved by a PENDING request (only an APPLIED
    one writes a REDEEMED ledger entry), so a user submitting redeem_credit
    on two leads before staff processes either could produce two pending
    requests against the same balance. Acceptable for this manual, low-volume
    admin workflow — staff see all pending requests together in Django Admin.
    """
    balance = get_balance(user)
    if balance <= 0:
        return None
    return RedemptionRequest.objects.create(
        user=user,
        amount_requested=balance,
        quote_request=quote_request,
    )


def credit_referral_reward(lead_instance: QuoteRequest | InspectionBooking) -> None:
    """Credit both sides of a referral the first time the referred person
    submits a qualifying quote or booking. No-ops silently for anonymous,
    non-referred, or already-rewarded users — this is called unconditionally
    from perform_create() on every lead submission.
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
        ReferralCredit.objects.create(
            user=referral.referrer,
            entry_type=CreditEntryType.EARNED_AS_REFERRER,
            amount=settings_row.referrer_reward_amount,
            referral=referral,
        )
        ReferralCredit.objects.create(
            user=user,
            entry_type=CreditEntryType.EARNED_AS_REFERRED,
            amount=settings_row.referred_reward_amount,
            referral=referral,
            note="Auto-applied to the triggering quote/booking.",
        )
        ReferralCredit.objects.create(
            user=user,
            entry_type=CreditEntryType.REDEEMED,
            amount=settings_row.referred_reward_amount,
            referral=referral,
            note="Auto-redeemed against the triggering quote/booking.",
        )
        RedemptionRequest.objects.create(
            user=user,
            amount_requested=settings_row.referred_reward_amount,
            quote_request=lead_instance if is_quote else None,
            status=RedemptionRequestStatus.APPLIED,
            admin_note="Auto-applied: referred person's reward on their own qualifying lead.",
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

    send_referral_reward_email(referral.referrer, settings_row.referrer_reward_amount)
