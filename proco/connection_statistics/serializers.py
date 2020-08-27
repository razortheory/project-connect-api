from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from unicef_restlib.fields import SeparatedReadWriteField

from proco.connection_statistics.models import CountryWeeklyStatus, RealTimeConnectivity, SchoolWeeklyStatus
from proco.schools.models import School


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


class RealTimeConnectivitySerializer(serializers.ModelSerializer):
    school = SeparatedReadWriteField(write_field=serializers.IntegerField(),
                                     read_field=serializers.StringRelatedField())

    class Meta:
        model = RealTimeConnectivity
        fields = (
            'school',
            'connectivity_speed',
            'connectivity_latency',
            'created',
        )
        read_only_fields = ('created', )

    def validate_school(self, school_id):
        schools = School.objects.filter(external_id=school_id)
        if not schools.exists():
            raise ValidationError(_('This school does not exist.'))
        return schools.first()
