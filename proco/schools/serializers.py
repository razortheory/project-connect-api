from rest_framework import serializers

from proco.locations.serializers import LocationSerializer
from proco.schools.models import School


class BaseSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = (
            'id', 'name', 'geopoint',
        )
        read_only_fields = fields


class ListSchoolSerializer(BaseSchoolSerializer):
    pass


class SchoolSerializer(BaseSchoolSerializer):
    location = LocationSerializer()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'location', 'gps_confidence', 'address', 'postal_code',
        )
