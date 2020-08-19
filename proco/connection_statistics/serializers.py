from rest_framework import serializers

from proco.connection_statistics.models import CountryWeeklyStatus, SchoolWeeklyStatus


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


class SchoolWeeklyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolWeeklyStatus
        fields = (
            'num_students',
            'num_teachers',
            'num_classroom',
            'num_latrines',
            'running_water',
            'electricity_availability',
            'computer_lab',
            'num_computers',
            'connectivity',
            'connectivity_status',
            'connectivity_speed',
            'connectivity_latency',
            'connectivity_availability',
        )
        read_only_fields = fields
