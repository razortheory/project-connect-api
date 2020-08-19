from rest_framework import serializers

from proco.connection_statistics.serializers import CountryWeeklyStatusSerializer
from proco.locations.models import Country, Location


class BaseCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id', 'name', 'code', 'flag',
            'map_preview', 'description', 'data_source', 'geometry',
        )
        read_only_fields = fields


class CountrySerializer(BaseCountrySerializer):
    pass


class ListCountrySerializer(BaseCountrySerializer):
    integration_status = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + ('integration_status',)

    def get_integration_status(self, instance):
        return instance.weekly_status.first().integration_status if instance.weekly_status.exists() else None


class DetailCountrySerializer(BaseCountrySerializer):
    statistics = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + ('schools', 'statistics')

    def get_statistics(self, instance):
        return CountryWeeklyStatusSerializer(instance.weekly_status.first()).data


class LocationSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Location
        fields = ('id', 'name', 'country', 'parent', 'geometry_simplified')
        read_only_fields = fields


class LocationLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'geometry_simplified')
        read_only_fields = fields
