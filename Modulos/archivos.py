"""Guarda y carga las personas de la conversación en archivos de texto

Los archivos se guardan en la carpeta Basededatos del proyecto
Formato del archivo (una persona por línea, separada por punto y coma):
    relacion;nombre;lugar
Ejemplo de "Basededatos/angela.txt":
    usuario;Angela;Caracas
    abuela;Alicia;Valencia
    primo;Luis;
   (si un dato no se conoce, queda vacio)
"""

import os
from Objetos.personas import Persona

# Carpeta Basededatos, buscada desde la ubicación de este archivo (Modulos/..),
# para que funcione sin importar desde qué carpeta se ejecute el programa.
CARPETA_DATOS = os.path.join(os.path.dirname(__file__), "..", "Basededatos")


def ruta(nombre_archivo):
    """devuelve la dirección completa del archivo dentro de la carpeta Basededatos

    Si la carpeta no existe (por ejemplo, la borraron), la crea

    Eficiencia: makedirs con exist_ok no repite trabajo si la carpeta ya existe
    """
    os.makedirs(CARPETA_DATOS, exist_ok=True)  # exist_ok: no da error si ya existe
    return os.path.join(CARPETA_DATOS, nombre_archivo)


class ManejadorArchivos:
    """Lee y escribe los archivos .txt con la información de las personas

    Eficiencia: Solo abre el archivo dos veces por sesión: al cargar (cuando el usuario dice su nombre) y al guardar (al despedirse), no en cada mensaje
    """

    def guardar(self, base, nombre_archivo):
        """Escribe todas las personas de la base en el archivo (modo 'w')

        Si el archivo ya existía, se reemplaza, porque la base ya incluye
        lo que se había cargado de él. Devuelve True si se pudo guardar

        Eficiencia: Recorre la lista de personas una sola vez y escribe todo de una vez
        """
        try:
            # "w" reescribe el archivo completo: así las personas no se repiten
            with open(ruta(nombre_archivo), "w", encoding="utf-8") as archivo:
                for persona in base.personas:
                    archivo.write(persona.a_linea())
            return True
        except OSError:
            print(f"Error: no se pudo guardar el archivo {nombre_archivo}.")
            return False

    def cargar(self, nombre_archivo):
        """Lee el archivo y devuelve una lista de objetos Persona

        Si el archivo no existe, devuelve None. Las líneas mal escritas
        (que no tienen 3 partes) se ignoran para no romper el programa

        Eficiencia: Lee el archivo una sola vez y recorre cada línea una vez
        """
        try:
            with open(ruta(nombre_archivo), "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
        except FileNotFoundError:  # usuario nuevo: todavía no tiene archivo
            return None

        personas = []
        for linea in lineas:
            partes = linea.strip().split(";")  # "abuela;Alicia;Valencia" -> 3 partes
            if len(partes) == 3:  # validación: se ignoran las líneas dañadas
                personas.append(Persona(partes[0], partes[1], partes[2]))
        return personas
