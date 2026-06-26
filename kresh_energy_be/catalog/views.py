from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import FAQ
from .models import CalculatorConfig
from .models import Project
from .models import Service
from .models import ServiceArea
from .models import Testimonial
from .serializers import CalculatorConfigSerializer
from .serializers import FAQSerializer
from .serializers import ProjectSerializer
from .serializers import ServiceAreaSerializer
from .serializers import ServiceSerializer
from .serializers import TestimonialSerializer


class ServiceViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    queryset = Service.objects.filter(is_active=True)
    lookup_field = "slug"


class ProjectViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(is_active=True)
    lookup_field = "slug"


class FAQViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = FAQSerializer
    queryset = FAQ.objects.filter(is_active=True)


class TestimonialViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = TestimonialSerializer
    queryset = Testimonial.objects.filter(is_active=True)


class ServiceAreaViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ServiceAreaSerializer
    queryset = ServiceArea.objects.filter(is_active=True)


class CalculatorConfigViewSet(ReadOnlyModelViewSet):
    """Serves the singleton calculator configuration as a single object."""

    permission_classes = [AllowAny]
    serializer_class = CalculatorConfigSerializer
    queryset = CalculatorConfig.objects.all()
    pagination_class = None

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(CalculatorConfig.get_instance())
        return Response(serializer.data)
