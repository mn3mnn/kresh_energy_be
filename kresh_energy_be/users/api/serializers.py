from rest_framework import serializers

from kresh_energy_be.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name", "email", "phone", "referral_code"]
