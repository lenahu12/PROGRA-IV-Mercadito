from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver

def sync_email(user):
    if not user.email:
        email_address = user.emailaddress_set.first()
        if email_address:
            user.email = email_address.email
            user.save()

@receiver(user_signed_up)
def populate_email(sender, request, user, **kwargs):
    if not user.email:
        email_address = user.emailaddress_set.first()
        if email_address:
            user.email = email_address.email
            user.save()

@receiver(user_logged_in)
def handle_login(sender, request, user, **kwargs):
    sync_email(user)
