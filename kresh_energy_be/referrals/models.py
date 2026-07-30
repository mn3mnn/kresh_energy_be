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


class ReferralDiscountStatus(models.TextChoices):
    AVAILABLE = "available", _("Available")
    APPLIED = "applied", _("Applied")


class ReferralDiscount(TimeStampedModel):
    """One row = one fixed-€ discount voucher, earned from a single
    qualifying referral. Used both for the referrer's own voucher (created
    AVAILABLE, applied later by the referrer picking it on a future quote)
    and the referred person's welcome voucher (usually created already
    APPLIED against the quote/booking that triggered it).

    There is no payment/invoicing system in this codebase — applying a
    voucher just links it to a QuoteRequest; no price is automatically
    deducted anywhere.
    """

    owner = models.ForeignKey(
        "users.User",
        verbose_name=_("Owner"),
        related_name="referral_discounts",
        on_delete=models.CASCADE,
    )
    referral = models.ForeignKey(
        Referral,
        on_delete=models.CASCADE,
        related_name="discounts",
    )
    amount = models.DecimalField(_("Amount (€)"), max_digits=8, decimal_places=2)
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=ReferralDiscountStatus.choices,
        default=ReferralDiscountStatus.AVAILABLE,
    )
    quote_request = models.ForeignKey(
        "leads.QuoteRequest",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applied_referral_discount",
    )
    applied_at = models.DateTimeField(_("Applied at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Referral discount")
        verbose_name_plural = _("Referral discounts")
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.owner} — €{self.amount} ({self.status})"
