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
    class Meta(BaseSchoolSerializer.Meta):
        fields = ('geopoint',)


class CSVSchoolsListSerializer(BaseSchoolSerializer):
    connectivity_status = serializers.SerializerMethodField()
    geopoint = GeoPointCSVField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = ('name', 'geopoint', 'connectivity_status')

    def get_connectivity_status(self, obj):
        if not obj.latest_status:
            return SchoolWeeklyStatus.CONNECTIVITY_STATUSES.unknown
        return obj.latest_status[0].connectivity_status


class ListSchoolSerializer(BaseSchoolSerializer):
    connectivity_status = serializers.SerializerMethodField()
    coverage_status = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'connectivity_status', 'coverage_status',
        )

    def get_connectivity_status(self, obj):
        if not obj.latest_status:
            return SchoolWeeklyStatus.CONNECTIVITY_STATUSES.unknown
        return obj.latest_status[0].connectivity_status

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
        return SchoolWeeklyStatusSerializer(instance.latest_status[0] if instance.latest_status else None).data

    def get_coverage_status(self, obj):
        return 'unknown'
