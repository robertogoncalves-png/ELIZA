"""Contiene las clases para guardar la información de las personas.

- Persona: alguien que el usuario mencionó (su abuela, su primo...).
- Usuario: hereda de Persona; es la persona que está hablando con ELIZA.
- BaseConocimiento: la lista de todas las personas de la conversación.
"""


class Persona:
    """Una persona mencionada en la conversación.

    Atributos:
        relacion (str): relación con el usuario, por ejemplo "abuela".
        nombre (str): nombre de la persona ("" si todavía no se sabe).
        lugar (str): lugar de origen o gentilicio ("" si todavía no se sabe).
    """

    def __init__(self, relacion, nombre="", lugar=""):
        """Constructor de la persona."""
        self.relacion = relacion
        self.nombre = nombre
        self.lugar = lugar

    def dato_faltante(self):
        """Dice qué dato le falta a la persona: "nombre", "lugar" o None si está completa."""
        if self.nombre == "":
            return "nombre"
        if self.lugar == "":
            return "lugar"
        return None

    def esta_completa(self):
        """Devuelve True si ya se conocen todos los datos."""
        return self.dato_faltante() == None

    def como_referirse(self):
        """Cómo ELIZA nombra a esta persona al hablar con el usuario: "tu abuela"."""
        return "tu " + self.relacion

    def a_linea(self):
        """Convierte la persona en una línea de texto para guardarla en el archivo.

        Formato: relacion;nombre;lugar   Ejemplo: abuela;Alicia;Valencia
        """
        return f"{self.relacion};{self.nombre};{self.lugar}\n"

    def __str__(self):
        """Muestra la persona de forma legible."""
        nombre = self.nombre
        if nombre == "":
            nombre = "(sin nombre)"
        lugar = self.lugar
        if lugar == "":
            lugar = "(sin lugar)"
        return f"{self.relacion.capitalize()}: {nombre}, de {lugar}"


class Usuario(Persona):
    """El usuario que habla con ELIZA. Hereda de Persona.

    Su relación siempre es "usuario". Sobrescribe como_referirse() y
    __str__() (polimorfismo).
    """

    def __init__(self, nombre="", lugar=""):
        """Constructor: llama al constructor del padre con la relación "usuario"."""
        super().__init__("usuario", nombre, lugar)

    def como_referirse(self):
        """Al usuario se le habla de "tú"."""
        return "tú"

    def nombre_archivo(self):
        """Nombre del archivo donde se guarda la conversación del usuario.

        Si no ha dado su nombre, el archivo es "usuario.txt".
        """
        if self.nombre == "":
            return "usuario.txt"
        return self.nombre.lower() + ".txt"  

    def __str__(self):
        """Muestra al usuario de forma legible."""
        return "(Tú) " + super().__str__()


class BaseConocimiento:
    """Guarda la lista de personas referenciadas en la conversación.

    El usuario siempre está en la posición 0 de la lista.
    """

    def __init__(self):
        """Crea la base con un usuario vacío."""
        self.usuario = Usuario()
        self.personas = [self.usuario] 

    def buscar(self, relacion):
        """Busca una persona por su relación. Devuelve la Persona o None."""
        for persona in self.personas:
            if persona.relacion == relacion:
                return persona
        return None

    def agregar(self, relacion):
        """Agrega una persona nueva si no existía y la devuelve.

        Si ya existía, devuelve la que estaba (no la repite).
        """
        persona = self.buscar(relacion)
        if persona == None: 
            persona = Persona(relacion)
            self.personas.append(persona)
        return persona

    def primera_incompleta(self):
        """Devuelve la primera persona (que no sea el usuario) con datos faltantes.

        Devuelve None si todas están completas.
        """
        for persona in self.personas[1:]:  
            if not persona.esta_completa():
                return persona
        return None

    def combinar(self, personas_archivo):
        """Mezcla las personas leídas del archivo con las de la conversación actual.

        La informacion de la conversacion actual tiene prioridad (es la más
        reciente): solo se copian del archivo los datos que hoy están vacíos.
        """
        for vieja in personas_archivo:
            actual = self.agregar(vieja.relacion)
            if actual.nombre == "": 
                actual.nombre = vieja.nombre
            if actual.lugar == "":
                actual.lugar = vieja.lugar

    def __str__(self):
        """Muestra todas las personas, una por línea."""
        texto = ""
        for persona in self.personas:
            texto += "  " + str(persona) + "\n"
        return texto
