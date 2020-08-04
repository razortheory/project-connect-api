from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core import validators
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from templated_email import send_templated_mail

from proco.custom_auth.generators import EmailConfirmTokenGenerator


class ResetPasswordMixin(models.Model):
    reset_password_email_template = 'auth/reset_password.html'
    reset_password_token_generator = default_token_generator

    class Meta:
        abstract = True

    def get_password_reset_url(self):
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = self.reset_password_token_generator.make_token(self)
        return reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

    def send_reset_password_email(self):
        self.email_user(self.reset_password_email_template)


class ConfirmAccountManagerMixin(object):
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_confirmed', True)
        return super(ConfirmAccountManagerMixin, self).create_superuser(username, email, password, **extra_fields)


class ConfirmAccountMixin(models.Model):
    confirm_account_email_template = 'auth/confirm_account.html'
    confirm_account_token_generator = EmailConfirmTokenGenerator()

    is_confirmed = models.BooleanField(_('confirmed'), default=False,
                                       help_text=_('Designates whether this user confirm his account.'))

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        is_new = not self.pk

        super(ConfirmAccountMixin, self).save(force_insert, force_update, using, update_fields)

        if is_new and not self.is_confirmed:
            self.send_confirm_account_email()

    def get_confirm_account_url(self):
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = self.confirm_account_token_generator.make_token(self)
        return reverse('account_confirm', kwargs={'uidb64': uid, 'token': token})

    def send_confirm_account_email(self):
        self.email_user(self.confirm_account_email_template)


class ApplicationUserManager(ConfirmAccountManagerMixin, UserManager):
    pass


class ApplicationUser(AbstractBaseUser, PermissionsMixin, ResetPasswordMixin, ConfirmAccountMixin):

    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only letters, numbers ' 'and @/./+/-/_ characters.'),
            ),
        ],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = ApplicationUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # Set True before inherit
        abstract = False

    def save(self, *args, **kwargs):
        if not self.email:
            # Unique constraint doesn't work correctly with empty string. So we need to forcibly set email to None.
            self.email = None

        super(ApplicationUser, self).save(*args, **kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, template_name, extra_context=None, **kwargs):
        """
        Sends an email to this User.
        """
        if not self.email:
            return

        context = {
            'user': self,
            'site': Site.objects.get_current(),
        }
        context.update(extra_context or {})

        send_templated_mail(template_name, settings.DEFAULT_FROM_EMAIL, [self.email], context, **kwargs)
