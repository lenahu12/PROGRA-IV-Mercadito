from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from decouple import config

class Command(BaseCommand):
    help = "Inicializa SocialApp para Google"

    def handle(self, *args, **kwargs):
        site = Site.objects.get(id=config("SITE_ID", default=1, cast=int))

        app, created = SocialApp.objects.get_or_create(
            provider="google",
            name="Google Login",
            client_id=config("GOOGLE_CLIENT_ID"),
            secret=config("GOOGLE_SECRET"),
        )
        app.sites.add(site)

        if created:
            self.stdout.write(self.style.SUCCESS("✅ SocialApp de Google creado"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ SocialApp de Google ya existía"))
