from rest_framework import serializers

from proco.connection_statistics.models import CountryWeeklyStatus
from proco.connection_statistics.serializers import CountryWeeklyStatusGraphSerializer
from proco.locations.models import Country


class BaseCountrySerializer(serializers.ModelSerializer):
    map_preview = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = (
            'id', 'name', 'code', 'flag',
            'map_preview', 'description', 'data_source',
        )
        read_only_fields = fields

    def get_map_preview(self, instance):
        if not instance.map_preview:
            return ''

        request = self.context.get('request')
        photo_url = instance.map_preview.url
        return request.build_absolute_uri(photo_url)


class CountrySerializer(BaseCountrySerializer):
    pass


class BoundaryListCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id', 'geometry_simplified',
        )
        read_only_fields = fields


class ListCountrySerializer(BaseCountrySerializer):
    integration_status = serializers.SerializerMethodField()
    schools_with_data_percentage = serializers.SerializerMethodField()
    schools_total = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + (
            'integration_status', 'date_of_join', 'schools_with_data_percentage', 'schools_total',
        )

    def get_integration_status(self, instance):
        return instance.latest_status[0].integration_status if instance.latest_status else None

    def get_schools_total(self, instance):
        return instance.latest_status[0].schools_total if instance.latest_status else None

    def get_date_of_join(self, instance):
        return instance.first_status[0].created if instance.first_status else None

    def get_schools_with_data_percentage(self, instance):
        return instance.latest_status[0].schools_with_data_percentage if instance.latest_status else None


class DetailCountrySerializer(BaseCountrySerializer):
    statistics = serializers.SerializerMethodField()

    class Meta(BaseCountrySerializer.Meta):
        fields = BaseCountrySerializer.Meta.fields + ('statistics', 'geometry')

    def get_statistics(self, instance):
        status = instance.latest_status[0] if instance.latest_status else None
        if status:
            status.previous_week_exists = CountryWeeklyStatus.objects.filter(country=instance).count() > 1
        return CountryWeeklyStatusGraphSerializer(status).data
