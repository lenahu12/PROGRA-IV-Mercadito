from rest_framework.routers import DefaultRouter
from .views import UserViewSet, user_form, logout_view
from django.urls import path

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = router.urls + [
    path("form/", user_form, name="user_form"),
]