
# from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_email_verification_code(email, verification_code, username):
    subject = 'Verify Your Email Address'

    html_message = render_to_string('Auth_email/verify-email.html', {'verification_code': verification_code, 'username': username})
    
    # Create the email with a custom sender name
    from_email = f'TodoMaster <{settings.EMAIL_HOST_USER}>'
    
    email_message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=from_email,
        to=[email]
    )
    email_message.attach_alternative(html_message, "text/html")
    
    email_message.send()

def resend_email_verification_code(email, verification_code, username):
    subject = 'Verify Your Email Address'

    html_message = render_to_string('Auth_email/resend-verify-email.html', {'verification_code': verification_code, 'username': username})
    
    # Create the email with a custom sender name
    from_email = f'TodoMaster <{settings.EMAIL_HOST_USER}>'
    
    email_message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=from_email,
        to=[email]
    )
    email_message.attach_alternative(html_message, "text/html")
    
    email_message.send()


def send_password_reset_code(email, reset_code,username):
    subject = 'Get a new TodoMaster account Password'

    html_message = render_to_string('Auth_email/password_reset_email.html', {'reset_code': reset_code,'username':username})

    from_email = f'TodoMaster <{settings.EMAIL_HOST_USER}>'

    # Create the email
    email_message = EmailMultiAlternatives(
        subject=subject,
        body='',  
        from_email=from_email,
        to=[email]
    )
    email_message.attach_alternative(html_message, "text/html")

    email_message.send()
