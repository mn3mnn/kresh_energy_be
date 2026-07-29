from django.contrib.auth.models import AbstractUser
from django.db.models import SET_NULL
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import ForeignKey
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Excludes visually-ambiguous characters (0/O, 1/I) from generated referral codes.
REFERRAL_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
REFERRAL_CODE_LENGTH = 8


class User(AbstractUser):
    """
    Default custom user model for Kresh Energy BE.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    # No default region: numbers must include an explicit country code
    # (e.g. "+49 151 2345678") so any country validates correctly, not just
    # one assumed default.
    phone = PhoneNumberField(_("Phone number"), blank=True)
    referral_code = CharField(
        _("My referral code"),
        max_length=16,
        unique=True,
        blank=True,
        help_text=_("Auto-generated on first save; shared with referred friends."),
    )
    referred_by = ForeignKey(
        "self",
        verbose_name=_("Referred by"),
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="referred_users",
    )
    referral_reward_granted = BooleanField(
        _("Referral reward already granted"),
        default=False,
        help_text=_(
            "Set once this user's referrer has been credited for referring them "
            "(fires on this user's first quote/booking submission, not on signup).",
        ),
    )

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_unique_referral_code()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_unique_referral_code(cls) -> str:
        for _attempt in range(10):
            code = get_random_string(REFERRAL_CODE_LENGTH, REFERRAL_CODE_ALPHABET)
            if not cls.objects.filter(referral_code=code).exists():
                return code
        msg = "Could not generate a unique referral code after 10 attempts."
        raise RuntimeError(msg)
