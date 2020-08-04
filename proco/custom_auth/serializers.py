from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.hashers import make_password

from rest_framework import fields, serializers
from rest_framework.settings import api_settings


class PasswordField(fields.CharField):
    def __init__(self, **kwargs):
        style = {
            'input_type': 'password',
        }
        style.update(kwargs.get('style', {}))
        kwargs['style'] = style
        super(PasswordField, self).__init__(**kwargs)


class SetPasswordMixin(serializers.Serializer):
    password = PasswordField(required=True, write_only=True)

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return make_password(value)


class UserSerializer(SetPasswordMixin, serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'url', 'username', 'email', 'password', 'first_name', 'last_name')


class LoginSerializer(serializers.Serializer):
    fail_login_message = ''

    def authenticate(self):
        user = authenticate(**self.validated_data)
        if not user:
            raise serializers.ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [self.fail_login_message],
            })
        return user


class UsernameLoginSerializer(LoginSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    fail_login_message = 'Invalid username or password.'


class ResetPasswordByEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ['email']
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super(ResetPasswordByEmailSerializer, self).__init__(*args, **kwargs)

    def send_reset_password_email(self):
        try:
            user = self.Meta.model.objects.get(email=self.validated_data.get('email'))
        except self.Meta.model.DoesNotExist:
            return

        user.send_reset_password_email()
