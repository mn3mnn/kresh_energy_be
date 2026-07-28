from django.conf import settings
from django.core.mail import mail_managers
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from kresh_energy_be.users.models import User

from .models import Referral
from .models import ReferralRewardSettings
from .models import RedemptionRequest
from .serializers import ReferralCodeCheckSerializer
from .serializers import ReferralDashboardSerializer
from .serializers import RedemptionRequestCreateSerializer
from .services import get_balance
from .services import request_redemption


class ReferralRateThrottle(AnonRateThrottle):
    scope = "referrals"


class ReferralCodeCheckView(APIView):
    """POST /api/referrals/check-code/ — existence check only, no info leak
    beyond validity (no expiry per scope, self-referral is checked here too
    when the caller is authenticated)."""

    permission_classes = [AllowAny]
    throttle_classes = [ReferralRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ReferralCodeCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"].strip()

        referrer = User.objects.filter(referral_code__iexact=code).first()
        valid = referrer is not None
        if valid and request.user.is_authenticated and referrer.pk == request.user.pk:
            valid = False

        return Response({"valid": valid})


class MyReferralDashboardView(APIView):
    """GET /api/referrals/me/ — the signed-in referrer's own dashboard data."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        settings_row = ReferralRewardSettings.get_instance()

        referrals = Referral.objects.filter(referrer=user).select_related(
            "referred_user",
        )
        redemption_requests = RedemptionRequest.objects.filter(user=user)

        # True when this user was themselves referred and hasn't yet
        # triggered their own reward (fires on their first qualifying
        # quote/booking, not on signup — see credit_referral_reward()).
        # Surfaced so the frontend can show "you have a reward waiting"
        # before that first submission.
        referred_pending = bool(
            user.referred_by_id
            and not user.referral_reward_granted
            and settings_row.is_active,
        )

        data = {
            "referral_code": user.referral_code,
            "referral_link": f"{settings.FRONTEND_URL}/refer?ref={user.referral_code}",
            "balance": get_balance(user),
            "referrals": referrals,
            "reward_amounts": {
                "referrer": settings_row.referrer_reward_amount,
                "referred": settings_row.referred_reward_amount,
            },
            "redemption_requests": redemption_requests,
            "referred_pending": referred_pending,
        }
        return Response(ReferralDashboardSerializer(data).data)


class RedemptionRequestViewSet(CreateModelMixin, GenericViewSet):
    """POST /api/referrals/redemptions/ — a referrer asks to apply their
    credit balance toward a (future) quote. No payment system exists, so
    this only creates a PENDING record for staff to honor manually in
    Django Admin (see RedemptionRequestInline on QuoteRequestAdmin)."""

    permission_classes = [IsAuthenticated]
    serializer_class = RedemptionRequestCreateSerializer
    queryset = RedemptionRequest.objects.all()

    def perform_create(self, serializer):
        quote_request = serializer.validated_data.get("quote_request")
        redemption = request_redemption(self.request.user, quote_request=quote_request)
        if redemption is None:
            msg = "You have no referral credit balance to redeem."
            raise ValidationError(msg)

        serializer.instance = redemption
        mail_managers(
            subject=f"Referral credit redemption requested — {self.request.user.email}",
            message=(
                f"User: {self.request.user.email}\n"
                f"Amount requested: €{redemption.amount_requested}\n"
                f"Linked quote: {redemption.quote_request_id or 'none'}\n"
            ),
            fail_silently=True,
        )
