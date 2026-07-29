from django.core.mail import mail_managers
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import GenericViewSet

from kresh_energy_be.referrals.services import credit_referral_reward
from kresh_energy_be.referrals.services import request_redemption

from .emails import send_booking_confirmation_email
from .emails import send_quote_confirmation_email
from .models import InspectionBooking
from .models import QuoteRequest
from .serializers import InspectionBookingSerializer
from .serializers import QuoteRequestSerializer


def _maybe_request_redemption(lead_instance, quote_for_link=None):
    """If the submitter (already-registered referrer) asked to redeem their
    referral credit on this submission, create the PENDING request. No-op
    if they have no balance or didn't ask."""
    if not lead_instance.redeem_credit or lead_instance.submitted_by_id is None:
        return
    redemption = request_redemption(lead_instance.submitted_by, quote_request=quote_for_link)
    if redemption is None:
        return
    mail_managers(
        subject=f"Referral credit redemption requested — {lead_instance.submitted_by.email}",
        message=(
            f"User: {lead_instance.submitted_by.email}\n"
            f"Amount requested: €{redemption.amount_requested}\n"
            f"Requested via: {lead_instance._meta.verbose_name} #{lead_instance.pk}\n"
        ),
        fail_silently=True,
    )


class LeadRateThrottle(AnonRateThrottle):
    scope = "leads"


class QuoteRequestViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    throttle_classes = [LeadRateThrottle]
    serializer_class = QuoteRequestSerializer
    queryset = QuoteRequest.objects.all()

    def perform_create(self, serializer):
        submitted_by = (
            self.request.user if self.request.user.is_authenticated else None
        )
        quote = serializer.save(submitted_by=submitted_by)
        mail_managers(
            subject=f"New quote request — {quote.full_name}",
            message=(
                f"Name: {quote.full_name}\n"
                f"Phone: {quote.phone}\n"
                f"Email: {quote.email}\n"
                f"Address: {quote.address}\n"
                f"Notes: {quote.notes}\n"
            ),
            fail_silently=True,
        )
        send_quote_confirmation_email(quote)
        credit_referral_reward(quote)
        _maybe_request_redemption(quote, quote_for_link=quote)


class InspectionBookingViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    throttle_classes = [LeadRateThrottle]
    serializer_class = InspectionBookingSerializer
    queryset = InspectionBooking.objects.all()

    def perform_create(self, serializer):
        submitted_by = (
            self.request.user if self.request.user.is_authenticated else None
        )
        booking = serializer.save(submitted_by=submitted_by)
        mail_managers(
            subject=f"New inspection booking — {booking.full_name}",
            message=(
                f"Name: {booking.full_name}\n"
                f"Phone: {booking.phone}\n"
                f"Email: {booking.email}\n"
                f"Address: {booking.address}\n"
                f"Date: {booking.preferred_date} ({booking.time_slot})\n"
                f"Notes: {booking.notes}\n"
            ),
            fail_silently=True,
        )
        send_booking_confirmation_email(booking)
        credit_referral_reward(booking)
        _maybe_request_redemption(booking)
