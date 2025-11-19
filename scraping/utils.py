import requests
from bs4 import BeautifulSoup

def comparar_precios(nombre):
    url = f"https://www.cotodigital3.com.ar/sitios/coto/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return f"Comparar precios de {nombre}: simulación de scraping"