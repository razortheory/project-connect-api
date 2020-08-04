from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache


@never_cache
def account_confirm(request, uidb64=None, token=None,
                    template_name='custom_auth/account_confirm.html',
                    token_generator=default_token_generator,
                    current_app=None, extra_context=None):

    UserModel = get_user_model()  # noqa S101
    if uidb64 is None or token is None:
        raise RuntimeError('uidb64 or token should be provided')

    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_confirmed = True
        user.save(update_fields=['is_confirmed'])
        validlink = True
        title = _('Account confirmed successfully')
    else:
        validlink = False
        title = _('Account confirmed unsuccessfully')

    context = {
        'title': title,
        'validlink': validlink,
    }

    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)
