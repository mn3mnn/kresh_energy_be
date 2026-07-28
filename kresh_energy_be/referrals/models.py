from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class ReferralRewardSettings(TimeStampedModel):
    """Admin-editable reward amounts (singleton, pk=1). Mirrors CalculatorConfig."""

    referrer_reward_amount = models.DecimalField(
        _("Referrer reward (€)"),
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_("Credited to the referrer when a referred person qualifies."),
    )
    referred_reward_amount = models.DecimalField(
        _("Referred-person reward (€)"),
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text=_(
            "Auto-applied as a discount on the referred person's own "
            "qualifying quote/booking.",
        ),
    )
    is_active = models.BooleanField(_("Referral program active"), default=True)

    class Meta:
        verbose_name = _("Referral reward settings")
        verbose_name_plural = _("Referral reward settings")

    def __str__(self) -> str:
        return "Referral reward settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce a single row
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # The singleton is never deleted.
        pass

    @classmethod
    def get_instance(cls) -> "ReferralRewardSettings":
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class ReferralStatus(models.TextChoices):
    SIGNED_UP = "signed_up", _("Signed up")
    QUALIFIED = "qualified", _("Lead submitted")
    REWARDED = "rewarded", _("Rewarded")


class Referral(TimeStampedModel):
    """One row per successfully-referred person; links referrer <-> referred_user."""

    referrer = models.ForeignKey(
        "users.User",
        verbose_name=_("Referrer"),
        related_name="referrals_made",
        on_delete=models.CASCADE,
    )
    referred_user = models.OneToOneField(
        "users.User",
        verbose_name=_("Referred user"),
        related_name="referral_received",
        on_delete=models.CASCADE,
    )
    code_used = models.CharField(_("Code used at signup"), max_length=16)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=ReferralStatus.choices,
        default=ReferralStatus.SIGNED_UP,
    )
    qualifying_quote = models.ForeignKey(
        "leads.QuoteRequest",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    qualifying_booking = models.ForeignKey(
        "leads.InspectionBooking",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    rewarded_at = models.DateTimeField(_("Rewarded at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Referral")
        verbose_name_plural = _("Referrals")
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["referred_user"],
                name="one_referral_per_referred_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.referrer} → {self.referred_user} ({self.status})"


class CreditEntryType(models.TextChoices):
    EARNED_AS_REFERRER = "earned_referrer", _("Earned (referrer reward)")
    EARNED_AS_REFERRED = "earned_referred", _("Earned (referred-person reward)")
    REDEEMED = "redeemed", _("Redeemed")


class ReferralCredit(TimeStampedModel):
    """Ledger row. Balance = sum(EARNED_*) - sum(REDEEMED), per user."""

    user = models.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        related_name="referral_credits",
        on_delete=models.CASCADE,
    )
    entry_type = models.CharField(
        _("Entry type"),
        max_length=20,
        choices=CreditEntryType.choices,
    )
    amount = models.DecimalField(_("Amount (€)"), max_digits=8, decimal_places=2)
    referral = models.ForeignKey(
        Referral,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="credit_entries",
    )
    note = models.CharField(_("Note"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Referral credit")
        verbose_name_plural = _("Referral credits")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.user} — {self.get_entry_type_display()} — €{self.amount}"


class RedemptionRequestStatus(models.TextChoices):
    PENDING = "pending", _("Pending admin review")
    APPLIED = "applied", _("Applied by admin")
    REJECTED = "rejected", _("Rejected")


class RedemptionRequest(TimeStampedModel):
    """A referrer's request to apply their balance as a discount.

    There is no payment/invoicing system in this codebase, so this is a
    manual, admin-honored annotation — visible in Django Admin next to the
    linked QuoteRequest — rather than an automated deduction.
    """

    user = models.ForeignKey(
        "users.User",
        verbose_name=_("User"),
        related_name="redemption_requests",
        on_delete=models.CASCADE,
    )
    amount_requested = models.DecimalField(
        _("Amount requested (€)"),
        max_digits=8,
        decimal_places=2,
    )
    quote_request = models.ForeignKey(
        "leads.QuoteRequest",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="redemption_requests",
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=RedemptionRequestStatus.choices,
        default=RedemptionRequestStatus.PENDING,
    )
    admin_note = models.TextField(_("Admin note"), blank=True)

    class Meta:
        verbose_name = _("Redemption request")
        verbose_name_plural = _("Redemption requests")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.user} — €{self.amount_requested} ({self.status})"
