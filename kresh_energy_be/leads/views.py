from django.core.mail import mail_managers
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import GenericViewSet

from kresh_energy_be.referrals.services import credit_referral_reward

from .emails import send_booking_confirmation_email
from .emails import send_quote_confirmation_email
from .models import InspectionBooking
from .models import QuoteRequest
from .serializers import InspectionBookingSerializer
from .serializers import QuoteRequestSerializer


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
