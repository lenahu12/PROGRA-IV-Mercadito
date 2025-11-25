from django.urls import path
from . import views

urlpatterns = [
    path("session-expired/", views.session_expired, name="session_expired"),
    path("online/", views.online_users, name="online-users"),
]
