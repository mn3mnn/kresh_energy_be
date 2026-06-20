from rest_framework import serializers

from kresh_energy_be.common.serializers import TranslatedFieldsMixin

from .models import FAQ
from .models import Project
from .models import Service
from .models import ServiceArea
from .models import Testimonial


class ServiceSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    translated_fields = ("title", "summary", "description")

    class Meta:
        model = Service
        fields = ["id", "slug", "icon", "audience", "order"]


class ProjectSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    translated_fields = ("title", "description")

    class Meta:
        model = Project
        fields = [
            "id",
            "slug",
            "city",
            "size_kwp",
            "panel_count",
            "image",
            "date_completed",
            "audience",
            "is_featured",
            "order",
        ]


class FAQSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    translated_fields = ("question", "answer")

    class Meta:
        model = FAQ
        fields = ["id", "category", "order"]


class TestimonialSerializer(TranslatedFieldsMixin, serializers.ModelSerializer):
    translated_fields = ("role", "quote")

    class Meta:
        model = Testimonial
        fields = ["id", "author_name", "city", "rating", "avatar", "order"]


class ServiceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceArea
        fields = [
            "id",
            "name",
            "postal_code",
            "latitude",
            "longitude",
            "contact_phone",
            "contact_email",
            "order",
        ]
