from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import hashlib
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.template import Context


def get_future_date(days_fwd):

    return timezone.now() + timedelta(days=days_fwd)


def get_expire_date():

    return get_future_date(settings.VERIFICATION_EXPIRE_DAYS)


def get_verification_code(email):
    return hashlib.md5((email + str(timezone.now())).encode('utf-8')).hexdigest()


def send_verification_email(host, verification_code, email):

    link = "".join([host, verification_code])

    email_params = {'registration_link': link, 'verification_code': verification_code}
    html_message = get_template('registration/verify_email.html').render(email_params)
    text_message = get_template('registration/email_text.txt').render(email_params)
    email = EmailMultiAlternatives('Confirm Your Email', text_message,
                                   from_email=settings.EMAIL_HOST_USER, to=[email])
    email.attach_alternative(html_message, "text/html")
    email.send()
