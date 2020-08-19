from rest_framework import serializers

from proco.connection_statistics.serializers import SchoolWeeklyStatusSerializer
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
    statistics = serializers.SerializerMethodField()

    class Meta(BaseSchoolSerializer.Meta):
        fields = BaseSchoolSerializer.Meta.fields + (
            'location', 'statistics', 'gps_confidence', 'address', 'postal_code',
        )

    def get_statistics(self, instance):
        return SchoolWeeklyStatusSerializer(instance.weekly_status.first()).data
