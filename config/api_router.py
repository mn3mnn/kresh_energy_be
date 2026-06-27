from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from kresh_energy_be.assistant.views import AssistantChatView
from kresh_energy_be.catalog.views import CalculatorConfigViewSet
from kresh_energy_be.catalog.views import FAQViewSet
from kresh_energy_be.catalog.views import ProjectViewSet
from kresh_energy_be.catalog.views import ServiceAreaViewSet
from kresh_energy_be.catalog.views import ServiceViewSet
from kresh_energy_be.catalog.views import TestimonialViewSet
from kresh_energy_be.leads.views import InspectionBookingViewSet
from kresh_energy_be.leads.views import QuoteRequestViewSet
from kresh_energy_be.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("services", ServiceViewSet, basename="service")
router.register("projects", ProjectViewSet, basename="project")
router.register("faqs", FAQViewSet, basename="faq")
router.register("testimonials", TestimonialViewSet, basename="testimonial")
router.register("service-areas", ServiceAreaViewSet, basename="servicearea")
router.register(
    "calculator-config",
    CalculatorConfigViewSet,
    basename="calculator-config",
)
router.register("quotes", QuoteRequestViewSet, basename="quote")
router.register("bookings", InspectionBookingViewSet, basename="booking")


app_name = "api"
urlpatterns = [
    *router.urls,
    path("assistant/chat/", AssistantChatView.as_view(), name="assistant-chat"),
]
