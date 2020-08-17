from rest_framework import serializers

from proco.locations.serializers import CountrySerializer, LocationSerializer
from proco.schools.models import School


class SchoolSerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    location = LocationSerializer()

    class Meta:
        model = School
        fields = (
            'id', 'name', 'country', 'location', 'timezone', 'geopoint', 'gps_confidence',
            'altitude', 'address', 'postal_code', 'email', 'education_level', 'environment', 'school_type',
        )
        read_only_fields = fields
