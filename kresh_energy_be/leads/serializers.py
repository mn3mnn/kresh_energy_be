from rest_framework import serializers

from .models import InspectionBooking
from .models import QuoteRequest
from .models import QuoteRoofPhoto


class QuoteRoofPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRoofPhoto
        fields = ["id", "image"]


class QuoteRequestSerializer(serializers.ModelSerializer):
    roof_photos = QuoteRoofPhotoSerializer(many=True, read_only=True)
    roof_photo_uploads = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = QuoteRequest
        fields = [
            "id",
            "full_name",
            "phone",
            "email",
            "address",
            "notes",
            "electricity_bill",
            "meter_photo",
            "calc_monthly_bill",
            "calc_system_size_kwp",
            "calc_roof_type",
            "wants_battery",
            "wants_ev_charger",
            "locale",
            "roof_photos",
            "roof_photo_uploads",
            "redeem_credit",
            "created",
        ]
        read_only_fields = ["id", "created"]

    def create(self, validated_data):
        uploads = validated_data.pop("roof_photo_uploads", [])
        quote = QuoteRequest.objects.create(**validated_data)
        QuoteRoofPhoto.objects.bulk_create(
            [QuoteRoofPhoto(quote=quote, image=image) for image in uploads],
        )
        return quote


class InspectionBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionBooking
        fields = [
            "id",
            "full_name",
            "phone",
            "email",
            "address",
            "preferred_date",
            "time_slot",
            "notes",
            "locale",
            "redeem_credit",
            "created",
        ]
        read_only_fields = ["id", "created"]
