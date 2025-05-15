from datetime import date
from rest_framework import serializers
from .models import Livestock


class LivestockSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Livestock
        fields = ["__all__", "age"]
        fields = ["id", "category", "tag_id", "specie", "birth_year", "age", "image", "registered_at"]

    def get_age(self, obj):
        return date.today().year - obj.birth_year
