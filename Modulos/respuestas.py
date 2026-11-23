"""Arma los mensajes que eliza le responde al usuario"""

from Objetos.frases import GrupoSalida
from Objetos.personas import Usuario


class ConstructorRespuestas:
    """Elige y arma la respuesta de ELIZA.

    Atributos:
        grupos (dict): nombre del grupo -> GrupoSalida (de salida.json).
        preguntas_nombre_usuario, preguntas_nombre_relacion,
        preguntas_lugar_usuario, preguntas_lugar_relacion (GrupoSalida):
            preguntas para completar los datos (de personas.json y lugares.json).
        confirmaciones (GrupoSalida): mensajes para decir que un dato se guardo.
    """

    def __init__(self, datos_salida, datos_personas, datos_lugares):
        """Crea los grupos de salida a partir de los diccionarios de la API."""
        self.grupos = {}
        for nombre in datos_salida:
            info = datos_salida[nombre]
            self.grupos[nombre] = GrupoSalida(nombre, info["Prioridad"], info["Frases clave"])

        self.preguntas_nombre_usuario = GrupoSalida(
            "Nombre del usuario", 0, datos_personas["Preguntar usuario"]["Frases clave"])
        self.preguntas_nombre_relacion = GrupoSalida(
            "Nombre de la relación", 0, datos_personas["Preguntar relación"]["Frases clave"])
        self.preguntas_lugar_usuario = GrupoSalida(
            "Lugar del usuario", 0, datos_lugares["Preguntar usuario"]["Frases clave"])
        self.preguntas_lugar_relacion = GrupoSalida(
            "Lugar de la relación", 0, datos_lugares["Preguntar relación"]["Frases clave"])
        self.confirmaciones = GrupoSalida("Confirmación", 0, [
            "Gracias, continúa.",
            "Anotado, gracias. Continúa.",
            "Muy bien, lo tendré en cuenta. Continúa.",
            "Gracias por decírmelo. Sigamos.",
        ])

    def respuesta_de_grupo(self, nombre_grupo):
        """Devuelve un mensaje al azar del grupo indicado (por ejemplo "Pésame").

        Si el grupo no existe, usa el grupo "Conversacional".
        """
        if nombre_grupo in self.grupos:  # evita error si el nombre no existe
            return self.grupos[nombre_grupo].elegir_respuesta()
        return self.grupos["Conversacional"].elegir_respuesta()

    def preguntar(self, persona, dato):
        """Arma la pregunta para conseguir el dato que le falta a una persona.

        Para el usuario: "¿Cómo te llamas?" o "¿De dónde eres?".
        Para otra persona: "Háblame de tu abuela. ¿Cómo se llama?".
        """
        if isinstance(persona, Usuario):  # al usuario se le pregunta directo
            if dato == "nombre":
                return self.preguntas_nombre_usuario.elegir_respuesta()
            return self.preguntas_lugar_usuario.elegir_respuesta()

        if dato == "nombre":
            pregunta = self.preguntas_nombre_relacion.elegir_respuesta()
        else:
            pregunta = self.preguntas_lugar_relacion.elegir_respuesta()
        return f"Háblame de {persona.como_referirse()}. {pregunta}"

    def confirmar(self):
        """Mensaje para avisar que el dato se guardó."""
        return self.confirmaciones.elegir_respuesta()

    def mencionar_conocida(self, persona):
        """Mensaje cuando el usuario vuelve a nombrar a alguien que ya conocemos.

        Ejemplo: "¿Tu abuela llamada Alicia, de Valencia?"
        """
        if persona.relacion.endswith("a") or persona.relacion.endswith("á"):  # abuela, tía, mamá
            llamado = "llamada"
        else:
            llamado = "llamado"
        mensaje = f"¿{persona.como_referirse().capitalize()} {llamado} {persona.nombre}"
        if persona.lugar != "":
            mensaje += f", de {persona.lugar}"
        return mensaje + "?"
