from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import logout
from .models import UserActivity

EXCLUDE_PREFIXES = (
    "/static/",
    "/media/",
    "/admin/",
)

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Evitar hits innecesarios (y bloqueos) en rutas no críticas
        if request.path.startswith(EXCLUDE_PREFIXES):
            return self.get_response(request)

        if request.user.is_authenticated:
            try:
                UserActivity.objects.update_or_create(
                    user=request.user,
                    defaults={"last_seen": timezone.now()}
                )
            except OperationalError:
                print("⚠️ No se pudo registrar actividad por bloqueo de base.")
        else:
            # Evita el TypeError cuando es AnonymousUser
            pass

        return self.get_response(request)


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now_ts = timezone.now().timestamp()
            last = request.session.get("last_activity", now_ts)
            if now_ts - last > 1800:
                logout(request)
                request.session.flush()
                return redirect("session_expired")
            request.session["last_activity"] = now_ts
        return self.get_response(request)