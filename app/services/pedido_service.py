from app.schemas.pedido import Pedido

pedidos = []

def crear_pedido(pedido: Pedido):
    nuevo_pedido = {
        "id_pedido": len(pedidos) + 1,
        "usuario": pedido.usuario.model_dump(),
        "carrito": pedido.carrito.model_dump()
    }

    pedidos.append(nuevo_pedido)

    return {
        "mensaje": "Pedido registrado correctamente",
        "pedido": nuevo_pedido
    }