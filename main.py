"""Menu principal del programa ELIZA."""

from Modulos.eliza import Eliza
from Modulos.archivos import ManejadorArchivos


def pedir_opcion(minimo, maximo):
    """Pide un número entre minimo y maximo, validando la entrada.

    Si el usuario escribe letras o un número fuera de rango, se muestra
    el error y se vuelve a pedir (el programa no se cierra).
    """
    while True:
        texto = input("Elige una opción: ").strip()
        if not texto.isdigit():  # se revisa antes de int() para que nunca falle
            print(f"Error: debes escribir un número del {minimo} al {maximo}.")
            continue
        opcion = int(texto)
        if opcion < minimo or opcion > maximo:
            print(f"Error: la opción debe estar entre {minimo} y {maximo}.")
            continue
        return opcion


def ver_archivo():
    """Pide el nombre de un usuario y muestra las personas guardadas en su archivo."""
    nombre = input("Nombre del usuario (deja vacío para 'usuario'): ").strip()
    if nombre == "":
        nombre = "usuario"  # mismo nombre que usa ELIZA si nadie se presentó
    nombre_archivo = nombre.lower() + ".txt"
    personas = ManejadorArchivos().cargar(nombre_archivo)
    if personas == None:  # el usuario nunca ha hablado con ELIZA
        print(f"No existe el archivo {nombre_archivo}.")
        return
    print(f"\nPersonas guardadas en {nombre_archivo}:")
    for persona in personas:
        print("  " + str(persona))


def main():
    """Descarga los datos con la API y muestra el menú hasta que el usuario salga."""
    print("Conectando con el repositorio de frases...")
    eliza = Eliza()
    if not eliza.cargar_datos():  # sin las frases ELIZA no puede conversar
        print("No se pudieron cargar las frases. Revisa tu conexión a internet e intenta de nuevo.")
        return

    salir = False
    while not salir:
        print("\n===== ELIZA - Psicoterapeuta virtual =====")
        print("1. Comenzar una sesión")
        print("2. Ver las personas guardadas de un usuario")
        print("3. Salir")
        opcion = pedir_opcion(1, 3)
        if opcion == 1:
            eliza.reiniciar()  # empieza sin las personas de la sesión anterior
            eliza.conversar()
        elif opcion == 2:
            ver_archivo()
        else:
            print("¡Hasta pronto!")
            salir = True


main()
