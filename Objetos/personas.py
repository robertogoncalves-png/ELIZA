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

    Eficiencia: Solo guarda tres textos; sus métodos solo revisan esos datos.
    """

    def __init__(self, relacion, nombre="", lugar=""):
        """Constructor de la persona.

        Eficiencia: Solo guarda tres datos.
        """
        self.relacion = relacion
        self.nombre = nombre
        self.lugar = lugar

    def dato_faltante(self):
        """Dice qué dato le falta a la persona: "nombre", "lugar" o None si está completa.

        Eficiencia: Solo hace dos comparaciones.
        """
        if self.nombre == "":
            return "nombre"
        if self.lugar == "":
            return "lugar"
        return None

    def esta_completa(self):
        """Devuelve True si ya se conocen todos los datos.

        Eficiencia: Reutiliza dato_faltante() en vez de repetir las comparaciones.
        """
        return self.dato_faltante() == None

    def como_referirse(self):
        """Cómo ELIZA nombra a esta persona al hablar con el usuario: "tu abuela".

        Eficiencia: Solo une dos textos.
        """
        return "tu " + self.relacion

    def a_linea(self):
        """Convierte la persona en una línea de texto para guardarla en el archivo.

        Formato: relacion;nombre;lugar   Ejemplo: abuela;Alicia;Valencia

        Eficiencia: Arma la línea con un solo f-string.
        """
        return f"{self.relacion};{self.nombre};{self.lugar}\n"

    def __str__(self):
        """Muestra la persona de forma legible.

        Eficiencia: Solo revisa dos datos y arma un texto.
        """
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

    Eficiencia: Hereda todo de Persona y solo cambia lo necesario.
    """

    def __init__(self, nombre="", lugar=""):
        """Constructor: llama al constructor del padre con la relación "usuario".

        Eficiencia: Reutiliza el constructor del padre con super().
        """
        super().__init__("usuario", nombre, lugar)

    def como_referirse(self):
        """Al usuario se le habla de "tú".

        Eficiencia: Devuelve un texto fijo.
        """
        return "tú"

    def nombre_archivo(self):
        """Nombre del archivo donde se guarda la conversación del usuario.

        Si no ha dado su nombre, el archivo es "usuario.txt".

        Eficiencia: Solo hace una comparación y un lower().
        """
        if self.nombre == "":
            return "usuario.txt"
        return self.nombre.lower() + ".txt"  

    def __str__(self):
        """Muestra al usuario de forma legible.

        Eficiencia: Reutiliza el __str__ del padre.
        """
        return "(Tú) " + super().__str__()


class BaseConocimiento:
    """Guarda la lista de personas referenciadas en la conversación.

    El usuario siempre está en la posición 0 de la lista.

    Eficiencia: Las personas se guardan en una lista; como en una conversación se mencionan pocas personas, recorrerla es rápido.
    """

    def __init__(self):
        """Crea la base con un usuario vacío.

        Eficiencia: Crea la lista con un solo elemento.
        """
        self.usuario = Usuario()
        self.personas = [self.usuario] 

    def buscar(self, relacion):
        """Busca una persona por su relación. Devuelve la Persona o None.

        Eficiencia: Recorre la lista y se detiene apenas encuentra la relación.
        """
        for persona in self.personas:
            if persona.relacion == relacion:
                return persona
        return None

    def agregar(self, relacion):
        """Agrega una persona nueva si no existía y la devuelve.

        Si ya existía, devuelve la que estaba (no la repite).

        Eficiencia: Usa buscar() para no duplicar personas.
        """
        persona = self.buscar(relacion)
        if persona == None: 
            persona = Persona(relacion)
            self.personas.append(persona)
        return persona

    def primera_incompleta(self):
        """Devuelve la primera persona (que no sea el usuario) con datos faltantes.

        Devuelve None si todas están completas.

        Eficiencia: Se detiene en la primera persona incompleta.
        """
        for persona in self.personas[1:]:  
            if not persona.esta_completa():
                return persona
        return None

    def combinar(self, personas_archivo):
        """Mezcla las personas leídas del archivo con las de la conversación actual.

        La informacion de la conversacion actual tiene prioridad (es la más
        reciente): solo se copian del archivo los datos que hoy están vacíos.

        Eficiencia: Por cada persona del archivo hace una búsqueda en la lista; con pocas personas es rápido.
        """
        for vieja in personas_archivo:
            actual = self.agregar(vieja.relacion)
            if actual.nombre == "": 
                actual.nombre = vieja.nombre
            if actual.lugar == "":
                actual.lugar = vieja.lugar

    def __str__(self):
        """Muestra todas las personas, una por línea.

        Eficiencia: Recorre la lista una sola vez.
        """
        texto = ""
        for persona in self.personas:
            texto += "  " + str(persona) + "\n"
        return texto
