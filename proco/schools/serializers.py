from rest_framework import serializers

from proco.connection_statistics.serializers import SchoolWeeklyStatusSerializer
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
    statistics = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'statistics', 'gps_confidence', 'address', 'postal_code',
        )

    def get_statistics(self, instance):
        return SchoolWeeklyStatusSerializer(instance.weekly_status.first()).data
