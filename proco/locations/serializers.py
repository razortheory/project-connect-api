from rest_framework import serializers

from proco.locations.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id', 'name', 'code', 'flag',
            'map_preview', 'description', 'data_source', 'geometry_simplified',
        )
        read_only_fields = fields
