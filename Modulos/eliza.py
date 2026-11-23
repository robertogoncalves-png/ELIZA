"""Contiene la clase Eliza, que lleva la conversación con el usuario."""

from Modulos.api import ConexionAPI
from Modulos.archivos import ManejadorArchivos
from Modulos.respuestas import ConstructorRespuestas
from Objetos.frases import GrupoEntrada, separar_palabras
from Objetos.personas import BaseConocimiento, Usuario


class Eliza:
    """El chatbot ELIZA.

    Atributos:
        api (ConexionAPI): para descargar las frases de GitHub.
        archivos (ManejadorArchivos): para guardar y cargar personas.
        base (BaseConocimiento): personas de la conversación actual.
        grupos_entrada (list): los 12 GrupoEntrada ordenados por prioridad.
        grupo_despedida (GrupoEntrada): grupo de prioridad 1 (termina el programa).
        grupo_personas (GrupoEntrada): grupo de prioridad 3 (Freudiano, se revisa siempre).
        reconocedores (dict): GrupoEntrada para reconocer nombres, lugares y gentilicios.
        respuestas (ConstructorRespuestas): arma los mensajes de salida.
        pendiente_persona (Persona): persona a la que se le preguntó un dato.
        pendiente_dato (str): dato preguntado ("nombre" o "lugar") o None.

    Eficiencia: Las frases se descargan y se preparan una sola vez en cargar_datos(); en cada mensaje solo se buscan.
    """

    def __init__(self):
        """Constructor: crea los objetos auxiliares. Los datos se cargan con cargar_datos().

        Eficiencia: Solo crea objetos vacíos; lo pesado se hace en cargar_datos().
        """
        self.api = ConexionAPI()
        self.archivos = ManejadorArchivos()
        self.base = BaseConocimiento()
        self.grupos_entrada = []
        self.grupo_despedida = None
        self.grupo_personas = None
        self.reconocedores = {}
        self.respuestas = None
        self.pendiente_persona = None  # persona a la que ELIZA le hizo una pregunta 
        self.pendiente_dato = None     # dato que se le pregunto, ya nombre o lugar

    def cargar_datos(self):
        """Descarga los 4 JSON con la API y crea todos los grupos de frases.

        Devuelve True si todo se cargó bien, o False si hubo un error.

        Eficiencia: Descarga los 4 archivos una sola vez. Ordenar con dos for revisa 12 x 12 = 144 veces, que es muy poco.
        """
        entrada = self.api.descargar("entrada.json")
        salida = self.api.descargar("salida.json")
        personas = self.api.descargar("personas.json")
        lugares = self.api.descargar("lugares.json")
        if entrada == None or salida == None or personas == None or lugares == None:
            return False  # sin internet no hay frases

        # Grupos de entrada (los 12 grupos de frases Clave)
        desordenados = []
        for nombre in entrada:
            info = entrada[nombre]
            comodin = None
            if "Comodín" in info:  # solo algunos grupos usan *
                comodin = info["Comodín"]
            grupo = GrupoEntrada(nombre, info["Prioridad"], info["Frases clave"], comodin)
            desordenados.append(grupo)
            # Se reconocen por su accion del JSON, no por su nombre
            if "Acción" in info and info["Acción"] == "Fin del programa":
                self.grupo_despedida = grupo
            if "Acción" in info and info["Acción"] == "actualizar relaciones":
                self.grupo_personas = grupo

        # Se ordenan de prioridad 1 a 12 para revisarlos en ese orden
        for prioridad in range(1, len(desordenados) + 1):
            for grupo in desordenados:
                if grupo.prioridad == prioridad:
                    self.grupos_entrada.append(grupo)

        # Frases para reconocer nombres, lugares y gentilicios (todas usan '*')
        self.reconocedores["usuario"] = GrupoEntrada(
            "Reconocer usuario", 0, personas["Reconocer usuario"]["Frases clave"], "*")
        self.reconocedores["relacion"] = GrupoEntrada(
            "Reconocer relación", 0, personas["Reconocer relación"]["Frases clave"], "*")
        self.reconocedores["lugar"] = GrupoEntrada(
            "Reconocer lugar", 0, lugares["Reconocer lugar"]["Frases clave"], "*")
        self.reconocedores["gentilicio"] = GrupoEntrada(
            "Reconocer gentilicio", 0, lugares["Reconocer gentilicio"]["Frases clave"], "*")

        self.respuestas = ConstructorRespuestas(salida, personas, lugares)
        return True

    def reiniciar(self):
        """Borra la información de la conversación anterior para empezar una nueva.

        Eficiencia: Solo crea una base nueva.
        """
        self.base = BaseConocimiento()
        self.pendiente_persona = None
        self.pendiente_dato = None

    def conversar(self):
        """Ciclo principal de la conversación: lee, responde, y repite hasta la despedida.

        Escribir "/personas" muestra las personas guardadas hasta el momento.

        Eficiencia: Hace una sola llamada a responder() por cada mensaje.
        """
        print("\nELIZA: Hola, soy ELIZA. ¿Que te trae por aquí hoy?")
        print("       (Para terminar, despidete. Escribe /personas para ver lo que sé.)")
        terminar = False
        while not terminar:
            texto = input("Tú: ").strip()
            if texto == "/personas":  # comando para ver lo que ELIZA recuerda
                print(self.base)
                continue
            mensaje, terminar = self.responder(texto)
            print("ELIZA:", mensaje)

    def responder(self, texto):
        """Decide la respuesta de ELIZA para lo que escribió el usuario.

        Orden de revisión:
        1. Despedida (prioridad 1): guarda el archivo y termina.
        2. Personas (prioridad 3): SIEMPRE se revisan para registrar a quien se nombre.
        3. Si ELIZA había hecho una pregunta, se guarda la respuesta.
        4. Grupos de prioridad 1 a 12: se usa el primero que coincida.
        5. Si nada coincide: se pregunta un dato faltante o se conversa.
        Devuelve una tupla (mensaje, terminar).

        Eficiencia: Revisa los grupos en orden de prioridad y se detiene en el primero que coincide.
        """
        palabras = separar_palabras(texto)
        if len(palabras) == 0:  # validación: mensaje vacío
            return ("No escribiste nada. Puedes contarme lo que quieras.", False)

        # 1. Despedida
        frase, palabra = self.grupo_despedida.buscar(palabras)
        if frase != None:
            return (self.despedirse(), True)

        # 2. Personas (siempre)
        mencionadas = self.revisar_personas(palabras)

        # 3. Respuesta a una pregunta de ELIZA
        if self.pendiente_dato != None:
            return (self.guardar_dato(palabras), False)

        # 4. Grupos en orden de prioridad
        for grupo in self.grupos_entrada:
            frase, palabra = grupo.buscar(palabras)
            if frase != None:
                if grupo == self.grupo_personas:  # puede usar los datos ya guardados
                    return (self.respuesta_personas(mencionadas), False)
                return (self.respuestas.respuesta_de_grupo(grupo.nombre), False)

        # 5. Ninguna frase clave
        return (self.preguntar_o_conversar(), False)

    def revisar_personas(self, palabras):
        """Busca las Frases Clave de personas (prioridad 3) y registra a cada persona.

        "mi abuela" -> relación "abuela".  "es mi jefe" -> relación "jefe".
        Devuelve la lista de personas mencionadas en este mensaje.

        Eficiencia: Revisa las frases del Freudiano una vez, y agregar() evita guardar personas repetidas.
        """
        sinonimos = {"mamá": "madre", "papá": "padre"}  # misma persona, distinta palabra
        mencionadas = []
        for frase, palabra in self.grupo_personas.buscar_todas(palabras):
            if palabra != "":
                relacion = palabra.lower()  # viene del comodín: "es mi jefe" -> "jefe"
            else:
                relacion = frase
                for articulo in ["mi ", "la ", "el "]:  # "mi abuela" -> "abuela"
                    if relacion.startswith(articulo):
                        relacion = relacion[len(articulo):]
            if relacion in sinonimos:
                relacion = sinonimos[relacion]
            persona = self.base.agregar(relacion)
            if persona not in mencionadas:
                mencionadas.append(persona)
        return mencionadas

    def respuesta_personas(self, mencionadas):
        """Respuesta cuando el usuario nombra a un familiar (prioridad 3).

        Si ya conocemos el nombre de esa persona, se sobreescribe el mensaje
        Freudiano por uno como "¿Tu abuela llamada Alicia?".

        Eficiencia: Se detiene en la primera persona conocida.
        """
        for persona in mencionadas:
            if persona.nombre != "":
                return self.respuestas.mencionar_conocida(persona)
        return self.respuestas.respuesta_de_grupo(self.grupo_personas.nombre)

    def guardar_dato(self, palabras):
        """Guarda la respuesta del usuario al dato que ELIZA preguntó.

        Nombre: se buscan las frases para reconocer nombres ("me llamo *");
        si no hay ninguna, se presume que la primera palabra es el nombre.
        Lugar: se buscan las frases de lugar ("de *") y gentilicio ("es *");
        si no hay ninguna, se toma la última palabra.
        Si el dato es el nombre del usuario, se carga su archivo anterior.

        Eficiencia: Solo busca en el reconocedor que hace falta (nombre, o lugar y luego gentilicio).
        """
        persona = self.pendiente_persona
        dato = self.pendiente_dato
        self.pendiente_persona = None  # ya se respondió: se borra la pregunta
        self.pendiente_dato = None

        if dato == "nombre":
            if isinstance(persona, Usuario):
                reconocedor = self.reconocedores["usuario"]
            else:
                reconocedor = self.reconocedores["relacion"]
            frase, palabra = reconocedor.buscar(palabras)
            if frase == None:
                palabra = palabras[0]  # regla del enunciado: se presume la primera palabra
            persona.nombre = palabra.capitalize()
            if isinstance(persona, Usuario):
                return self.cargar_usuario()
        else:
            frase, palabra = self.reconocedores["lugar"].buscar(palabras)
            if frase == None:
                frase, palabra = self.reconocedores["gentilicio"].buscar(palabras)
            if frase == None:
                palabra = palabras[-1]  # en "Soy venezolana" el lugar va al final
            persona.lugar = palabra.capitalize()

        return self.respuestas.confirmar()

    def cargar_usuario(self):
        """Busca el archivo con el nombre del usuario y, si existe, carga sus datos.

        Los datos de la conversación actual tienen prioridad sobre los del archivo.

        Eficiencia: Lee el archivo una sola vez, cuando el usuario dice su nombre.
        """
        usuario = self.base.usuario
        personas_archivo = self.archivos.cargar(usuario.nombre_archivo())
        if personas_archivo == None:
            return f"Mucho gusto, {usuario.nombre}. " + self.respuestas.confirmar()
        self.base.combinar(personas_archivo)  # lo de hoy tiene prioridad sobre el archivo
        return (f"¡Qué bueno verte de nuevo, {usuario.nombre}! "
                "Recuerdo lo que me contaste la última vez. Continúa.")

    def preguntar_o_conversar(self):
        """Se usa cuando no hay ninguna Frase Clave en el mensaje.

        Primero pregunta lo que falte del usuario (nombre, luego lugar), después
        lo que falte de las demás personas, y si todo está completo usa un
        mensaje del grupo Conversacional (prioridad 0).

        Eficiencia: Primero revisa al usuario y solo si está completo recorre a las demás personas.
        """
        persona = self.base.usuario
        dato = persona.dato_faltante()
        if dato == None:  # el usuario está completo: se revisan las demás personas
            persona = self.base.primera_incompleta()
            if persona == None:
                return self.respuestas.respuesta_de_grupo("Conversacional")
            dato = persona.dato_faltante()

        self.pendiente_persona = persona
        self.pendiente_dato = dato
        return self.respuestas.preguntar(persona, dato)

    def despedirse(self):
        """Guarda la información en el archivo del usuario y devuelve la despedida.

        Eficiencia: El archivo se escribe una sola vez, al final, y no en cada mensaje.
        """
        mensaje = self.respuestas.respuesta_de_grupo(self.grupo_despedida.nombre)
        nombre_archivo = self.base.usuario.nombre_archivo()
        if self.archivos.guardar(self.base, nombre_archivo):
            mensaje += f"\n       (La sesión se guardó en el archivo {nombre_archivo})"
        return mensaje
