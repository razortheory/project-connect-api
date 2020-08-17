from rest_framework import serializers

from proco.locations.models import Country, Location


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id', 'name', 'code', 'flag',
            'map_preview', 'description', 'data_source', 'geometry',
        )
        read_only_fields = fields


class LocationSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'parent', 'geometry_simplified')
        read_only_fields = fields
