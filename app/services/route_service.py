from app.schemas.usuario import Usuario
from app.schemas.repartidor import Repartidor


# =====================================
# SERVICIO DE USUARIO
# =====================================

def crear_usuario(usuario: Usuario):

    return {
        "mensaje": "Usuario registrado correctamente",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "producto": usuario.producto,
            "ubicacion_actual": usuario.ubicacion_actual
        }
    }


# =====================================
# SERVICIO DE REPARTIDOR
# =====================================

def calculate_route(repartidor: Repartidor):

    ubicacion_inicial = repartidor.ubicacion_inicial
    algoritmo = repartidor.algoritmo

    if algoritmo == "fuerzaBruta":

        resultado = "Ejecutando Fuerza Bruta"

    elif algoritmo == "backtracking":

        resultado = "Ejecutando Backtracking"

    elif algoritmo == "divideVenceras":

        resultado = "Ejecutando Divide y Vencerás"

    else:

        raise ValueError("Algoritmo no válido")

    return {
        "ubicacion_inicial": ubicacion_inicial,
        "algoritmo": algoritmo,
        "resultado": resultado
    }