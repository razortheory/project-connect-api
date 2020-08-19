from rest_framework import serializers

from proco.connection_statistics.models import CountryWeeklyStatus


class CountryWeeklyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryWeeklyStatus
        fields = (
            'schools_total',
            'schools_connected',
            'schools_connectivity_unknown',
            'schools_connectivity_no',
            'schools_connectivity_moderate',
            'schools_connectivity_good',
            'connectivity_speed',
            'integration_status',
            'avg_distance_school',
        )
        read_only_fields = fields
