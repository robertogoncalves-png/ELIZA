"""Contiene las clases que representan los grupos de Frases Clave.

GrupoFrases es la clase padre, de ella heredan:
- GrupoEntrada: frases que se buscan en lo que escribe el usuario.
- GrupoSalida: mensajes que ELIZA puede responder.
"""

import random


def quitar_tildes(texto):
    """Devuelve el texto en minúsculas y sin tildes, para comparar palabras.

    Así "Adiós", "adios" y "ADIÓS" se consideran la misma palabra.
    """
    texto = texto.lower()
    cambios = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u"}
    for con_tilde in cambios:
        texto = texto.replace(con_tilde, cambios[con_tilde])
    return texto


def separar_palabras(texto):
    """Quita los signos de puntuación del texto y lo separa en una lista de palabras.

    Las palabras se devuelven tal como el usuario las escribió (con sus
    mayúsculas), para poder guardar nombres como "Alicia" correctamente.
    """
    signos = "¿?¡!.,;:\"()"  
    for signo in signos:
        texto = texto.replace(signo, " ")
    return texto.split()


class GrupoFrases:
    """Clase padre: un grupo de frases con un nombre y una prioridad.

    Atributos:
        nombre (str): nombre del grupo, por ejemplo "Pésame".
        prioridad (int): 1 es la más importante; 0 es el grupo conversacional.
        frases (list): lista de strings con las frases del grupo.
    """

    def __init__(self, nombre, prioridad, frases):
        """Constructor del grupo de frases."""
        self.nombre = nombre
        self.prioridad = prioridad
        self.frases = frases

    def __str__(self):
        """Muestra el grupo de forma legible."""
        return f"[{self.prioridad}] {self.nombre} ({len(self.frases)} frases)"


class GrupoEntrada(GrupoFrases):
    """Grupo de Frases Clave que se buscan dentro del texto del usuario.

    Hereda de GrupoFrases y agrega el comodín ('*'). Si una frase tiene el
    comodín, la palabra que viene justo después en el texto del usuario se
    guarda (por ejemplo "es mi *" con "él es mi jefe" guarda "jefe").
    """

    def __init__(self, nombre, prioridad, frases, comodin=None):
        """Constructor: llama al constructor del padre con super()."""
        super().__init__(nombre, prioridad, frases)
        self.comodin = comodin

    def buscar_frase(self, frase, palabras):
        """Busca UNA frase clave dentro de la lista de palabras del usuario.

        Devuelve una tupla (encontrada, palabra_comodin):
        - (False, "") si la frase no está.
        - (True, "") si está y no tiene comodín.
        - (True, "Alicia") si está y tiene comodín: la palabra siguiente.
        Si la frase tiene comodín pero el texto se acaba antes de la palabra,
        se considera que NO coincide (así lo pide el enunciado).
        """
        partes = quitar_tildes(frase).split()
        tiene_comodin = False
        if self.comodin != None and self.comodin in partes:
            tiene_comodin = True
            partes.remove(self.comodin)  

        # Versión de las palabras del usuario para comparar (minúscula y sin tildes)
        comparables = []
        for palabra in palabras:
            comparables.append(quitar_tildes(palabra))

        cantidad = len(partes)
        for i in range(len(comparables) - cantidad + 1):
            if comparables[i:i + cantidad] == partes:
                if not tiene_comodin:
                    return (True, "")
                siguiente = i + cantidad
                if siguiente < len(palabras):  
                    return (True, palabras[siguiente])
        return (False, "")

    def buscar(self, palabras):
        """Busca si ALGUNA frase del grupo está en el texto del usuario.

        Devuelve una tupla (frase, palabra_comodin) con la primera frase que
        coincida, o (None, "") si ninguna coincide.
        """
        for frase in self.frases:
            encontrada, palabra = self.buscar_frase(frase, palabras)
            if encontrada:
                return (frase, palabra)
        return (None, "")

    def buscar_todas(self, palabras):
        """Igual que buscar(), pero devuelve TODAS las frases que coinciden.

        Sirve para cuando el usuario menciona varias personas a la vez,
        por ejemplo "mi mamá y mi abuela". Devuelve una lista de tuplas.
        """
        encontradas = []
        for frase in self.frases:
            encontrada, palabra = self.buscar_frase(frase, palabras)
            if encontrada:
                encontradas.append((frase, palabra))
        return encontradas


class GrupoSalida(GrupoFrases):
    """Grupo de mensajes que ELIZA puede responder. Hereda de GrupoFrases."""

    def elegir_respuesta(self):
        """Elige uno de los mensajes del grupo al azar con el módulo random."""
        return random.choice(self.frases)
