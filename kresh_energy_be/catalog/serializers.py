from rest_framework import serializers

from kresh_energy_be.common.serializers import TranslatedFieldsMixin

from .models import FAQ
from .models import CalculatorConfig
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


class CalculatorConfigSerializer(serializers.ModelSerializer):
    """Numeric calculator assumptions for the frontend estimator.

    Decimal columns are exposed as ``FloatField`` so the JSON is numeric
    (``0.35`` rather than the string ``"0.35"`` DRF emits for DecimalField) —
    the calculator does arithmetic on these. The three roof factors are folded
    into a nested ``usable_roof_factor`` object to match the ``solar.ts`` shape.
    """

    electricity_price = serializers.FloatField(read_only=True)
    feed_in_tariff = serializers.FloatField(read_only=True)
    panel_kwp = serializers.FloatField(read_only=True)
    panel_area_m2 = serializers.FloatField(read_only=True)
    self_consumption_no_battery = serializers.FloatField(read_only=True)
    self_consumption_with_battery = serializers.FloatField(read_only=True)
    usable_roof_factor = serializers.SerializerMethodField()

    class Meta:
        model = CalculatorConfig
        fields = [
            "electricity_price",
            "feed_in_tariff",
            "specific_yield",
            "panel_kwp",
            "panel_area_m2",
            "base_consumption",
            "per_member_consumption",
            "ev_consumption",
            "self_consumption_no_battery",
            "self_consumption_with_battery",
            "usable_roof_factor",
        ]

    def get_usable_roof_factor(self, obj) -> dict[str, float]:
        return {
            "pitched": float(obj.usable_roof_factor_pitched),
            "flat": float(obj.usable_roof_factor_flat),
            "other": float(obj.usable_roof_factor_other),
        }
