from rest_framework import serializers

from proco.connection_statistics.models import SchoolWeeklyStatus
from proco.connection_statistics.serializers import SchoolWeeklyStatusSerializer
from proco.locations.fields import GeoPointCSVField
from proco.schools.models import School


class BaseSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = (
            'id', 'name', 'geopoint',
        )
        read_only_fields = fields


class SchoolPointSerializer(BaseSchoolSerializer):
    country_integration_status = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = ('geopoint', 'country_id', 'country_integration_status')

    def __init__(self, *args, **kwargs):
        self.countries_statuses = kwargs.pop('countries_statuses', None)
        super(SchoolPointSerializer, self).__init__(*args, **kwargs)

    def get_country_integration_status(self, obj):
        return self.countries_statuses[obj.country_id]


class CSVSchoolsListSerializer(BaseSchoolSerializer):
    connectivity_status = serializers.SerializerMethodField()
    geopoint = GeoPointCSVField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = ('name', 'geopoint', 'connectivity_status')

    def get_connectivity_status(self, obj):
        if not obj.last_weekly_status:
            return SchoolWeeklyStatus.CONNECTIVITY_STATUSES.unknown
        return obj.last_weekly_status.connectivity_status


class ListSchoolSerializer(BaseSchoolSerializer):
    connectivity_status = serializers.SerializerMethodField()
    coverage_status = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'connectivity_status', 'coverage_status',
        )

    def get_connectivity_status(self, obj):
        if not obj.last_weekly_status:
            return SchoolWeeklyStatus.CONNECTIVITY_STATUSES.unknown
        return obj.last_weekly_status.connectivity_status

    def get_coverage_status(self, obj):
        return 'unknown'


class SchoolSerializer(BaseSchoolSerializer):
    statistics = serializers.SerializerMethodField()
    coverage_status = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'statistics',
            'gps_confidence', 'address', 'postal_code',
            'admin_1_name', 'admin_2_name', 'admin_3_name', 'admin_4_name',
            'timezone', 'altitude', 'email', 'education_level', 'environment', 'school_type', 'coverage_status',
        )

    def get_statistics(self, instance):
        return SchoolWeeklyStatusSerializer(instance.last_weekly_status).data

    def get_coverage_status(self, obj):
        return 'unknown'
