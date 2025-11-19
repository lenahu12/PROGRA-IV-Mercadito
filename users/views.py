from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from .forms import UserForm
from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

def user_form(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/api/users/")  # redirige a la lista JSON
    else:
        form = UserForm()
    return render(request, "user_form.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('/')