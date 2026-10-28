from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

A_TipoPedido = Literal["MESA", "PARA_LLEVAR", "EVENTO"]
A_EstadoPedido = Literal["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "ANULADO"]


class A_DetallePedidoCreate(BaseModel):
    id_producto: int = Field(..., description="ID del producto solicitado")
    cantidad: int = Field(..., gt=0, description="Cantidad solicitada")


class A_PedidoCreate(BaseModel):
    """El precio y los totales NO se envían: los calcula la API (RN01)."""
    id_cliente: int = Field(..., description="ID del cliente")
    tipo_pedido: A_TipoPedido = Field(..., description="Tipo de pedido")
    observaciones: Optional[str] = Field(None, description="Observaciones")
    detalles: List[A_DetallePedidoCreate] = Field(..., min_length=1, description="Ítems del pedido")


class A_PedidoUpdate(BaseModel):
    """Datos de cabecera editables mientras el pedido no esté ENTREGADO/ANULADO (RN05)."""
    tipo_pedido: Optional[A_TipoPedido] = None
    observaciones: Optional[str] = None


class A_PedidoEstadoUpdate(BaseModel):
    estado: A_EstadoPedido = Field(..., description="Nuevo estado del pedido")


class A_DetallePedidoResponse(BaseModel):
    id_detalle: Optional[int] = None
    id_producto: int
    nombre_producto: Optional[str] = None
    cantidad: int
    precio_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class A_PedidoResponse(BaseModel):
    id_pedido: int
    fecha_pedido: str
    id_cliente: int
    id_usuario: int
    tipo_pedido: str
    estado: str
    total: float
    observaciones: Optional[str] = None
    detalles: List[A_DetallePedidoResponse] = []
    model_config = ConfigDict(from_attributes=True)
