from django.conf import settings

from rest_framework import serializers

from templated_email import send_templated_mail


class ContactSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True, max_length=256)
    organisation = serializers.CharField(required=True, max_length=256)
    purpose = serializers.CharField(required=True, max_length=256)
    message = serializers.CharField(required=True)

    class Meta:
        fields = ('full_name', 'organisation', 'purpose', 'message')

    def create(self, validated_data):
        send_templated_mail(
            '/contact_email', settings.DEFAULT_FROM_EMAIL, settings.CONTACT_MANAGERS, context=validated_data,
        )
        return validated_data
