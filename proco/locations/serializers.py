from rest_framework import serializers

from proco.connection_statistics.serializers import CountryWeeklyStatusSerializer
from proco.locations.models import Country


class BaseCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id', 'name', 'code', 'flag',
            'map_preview', 'description', 'data_source', 'geometry_simplified',
        )
        read_only_fields = fields


class CountrySerializer(BaseCountrySerializer):
    pass


class ListCountrySerializer(BaseCountrySerializer):
    integration_status = serializers.SerializerMethodField()
    date_of_join = serializers.SerializerMethodField()
    schools_with_data_percentage = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + (
            'integration_status', 'date_of_join', 'schools_with_data_percentage',
        )

    def get_integration_status(self, instance):
        return instance.latest_status[0].integration_status if instance.latest_status else None

    def get_date_of_join(self, instance):
        return getattr(instance, 'date_of_join', None)

    def get_schools_with_data_percentage(self, instance):
        return getattr(instance, 'schools_with_data_percentage', None)


class DetailCountrySerializer(BaseCountrySerializer):
    statistics = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + ('statistics', 'geometry')

    def get_statistics(self, instance):
        return CountryWeeklyStatusSerializer(instance.latest_status[0] if instance.latest_status else None).data
