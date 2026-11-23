"""Descarga los archivos JSON de frases clave desde GitHub usando requests."""

import requests


class ConexionAPI:
    """Se conecta al repositorio GitHub y descarga los JSON con las frases.

    Atributos:
        url_base (str): dirección donde están los archivos JSON.
    """

    def __init__(self):
        """Constructor con la dirección del repositorio."""
        self.url_base = "https://raw.githubusercontent.com/FernandoSapient/BPTSP05_2627-1/main/"

    def descargar(self, nombre_archivo):
        """Hace la solicitud GET a la API y devuelve el JSON como diccionario.

        Revisa que la respuesta sea correcta (código 200). Si no hay internet
        o la respuesta falla, devuelve None en vez de cerrar el programa.
        """
        url = self.url_base + nombre_archivo
        try:
            respuesta = requests.get(url, timeout=10)  # timeout: no esperar para siempre
        except requests.exceptions.RequestException:
            print(f"Error: no se pudo conectar a internet para descargar {nombre_archivo}.")
            return None

        if respuesta.status_code != 200:  # 200 = la respuesta llegó bien
            print(f"Error: la API respondió con el código {respuesta.status_code} para {nombre_archivo}.")
            return None

        try:
            return respuesta.json()
        except ValueError:
            print(f"Error: {nombre_archivo} no tiene formato JSON válido.")
            return None
