from pydantic import BaseModel


class PedidoItem(BaseModel):
    id: int
    name: str
    price: float
    category: str
    emoji: str
    cantidad: int


class Carrito(BaseModel):
    items: list[PedidoItem]
    subtotal: float
    delivery: float
    total: float


class UsuarioPedido(BaseModel):
    id: int
    nombre: str
    ubicacion_actual: str


class Pedido(BaseModel):
    usuario: UsuarioPedido
    carrito: Carrito