from dj_rest_auth.registration.serializers import RegisterSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from kresh_energy_be.users.models import User

from .emails import send_referral_signup_email
from .models import Referral
from .models import ReferralDiscount
from .models import ReferralStatus


class ReferralRegisterSerializer(RegisterSerializer):
    """Extends dj-rest-auth's registration to capture name, phone, and a
    referral code.

    The code may come from the request body or fall back to the `kresh_ref`
    cookie set when the visitor landed on a referral link. An unresolved or
    self-referencing code is silently ignored — no error, no expiry logic.

    Also overrides `username` to be optional: ACCOUNT_SIGNUP_FIELDS drops it
    (email-only signup, decision #13), but dj-rest-auth 7.2's
    `_signup_field_required()` still defaults a field to required when it's
    simply absent from allauth's SIGNUP_FIELDS dict — a library quirk, not
    something ACCOUNT_SIGNUP_FIELDS alone fixes. Leaving it blank is safe:
    allauth's own `populate_username()` auto-generates a unique one from the
    email when the submitted username is empty.
    """

    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    name = serializers.CharField(max_length=255)
    # No default region (see User.phone) — requires an explicit country code,
    # e.g. "+49 151 2345678"; rejects anything libphonenumber can't parse.
    phone = PhoneNumberField(required=False, allow_blank=True)
    referral_code = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        max_length=16,
    )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["name"] = self.validated_data.get("name", "")
        data["phone"] = self.validated_data.get("phone", "")
        return data

    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data.get("name", "")
        user.phone = self.cleaned_data.get("phone", "")

        code = (
            self.validated_data.get("referral_code")
            or request.COOKIES.get("kresh_ref")
            or ""
        ).strip()
        if code:
            referrer = (
                User.objects.filter(referral_code__iexact=code)
                .exclude(pk=user.pk)
                .first()
            )
            if referrer:
                user.referred_by = referrer

        user.save(update_fields=["name", "phone", "referred_by"])

        if user.referred_by_id:
            _referral, created = Referral.objects.get_or_create(
                referred_user=user,
                defaults={
                    "referrer": user.referred_by,
                    "code_used": code,
                    "status": ReferralStatus.SIGNED_UP,
                },
            )
            if created:
                send_referral_signup_email(user.referred_by)
        return user


class ReferralCodeCheckSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=16)


class ReferredPersonSerializer(serializers.Serializer):
    email_masked = serializers.SerializerMethodField()
    status = serializers.CharField()
    created = serializers.DateTimeField()
    reward_amount = serializers.SerializerMethodField()
    reward_status = serializers.SerializerMethodField()
    applied_at = serializers.SerializerMethodField()

    def get_email_masked(self, referral: Referral) -> str:
        email = referral.referred_user.email
        name, _sep, domain = email.partition("@")
        masked = name[:4] + "***" if name else "***"
        return f"{masked}@{domain}" if domain else masked

    def _referrer_discount(self, referral: Referral) -> ReferralDiscount | None:
        # `discounts` is prefetched on the queryset built in
        # MyReferralDashboardView — filter in Python to reuse the cache.
        for discount in referral.discounts.all():
            if discount.owner_id == referral.referrer_id:
                return discount
        return None

    def get_reward_amount(self, referral: Referral) -> str | None:
        discount = self._referrer_discount(referral)
        return discount.amount if discount else None

    def get_reward_status(self, referral: Referral) -> str:
        discount = self._referrer_discount(referral)
        if discount is None:
            return "pending"
        return discount.status

    def get_applied_at(self, referral: Referral):
        discount = self._referrer_discount(referral)
        return discount.applied_at if discount else None


class ReferralDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralDiscount
        fields = ["id", "amount", "status", "quote_request", "applied_at", "created"]


class ReferralDashboardSerializer(serializers.Serializer):
    """Assembled by the view, not a ModelSerializer — the shape spans
    User, Referral and ReferralDiscount."""

    referral_code = serializers.CharField()
    referral_link = serializers.CharField()
    referrals = ReferredPersonSerializer(many=True)
    # Explicit DecimalField child so both amounts render as "25.00", not a
    # bare JSON number "25" (which loses the trailing zeros on the frontend).
    reward_amounts = serializers.DictField(
        child=serializers.DecimalField(max_digits=8, decimal_places=2),
    )
    discounts = ReferralDiscountSerializer(many=True)
    referred_pending = serializers.BooleanField()
