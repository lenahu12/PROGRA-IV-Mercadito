from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import comparar_precios

class CompararPrecios(APIView):
    def get(self, request, nombre):
        resultado = comparar_precios(nombre)
        return Response({"resultado": resultado})