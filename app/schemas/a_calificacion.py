from typing import List, Optional
from pydantic import BaseModel, Field


class A_CalificacionProductoItem(BaseModel):
    id_producto: int = Field(..., description="ID del producto evaluado")
    nombre: str = Field(..., description="Nombre del producto")
    calificacion: int = Field(..., ge=1, le=5, description="Puntuación (1-5)")


class A_CalificacionCreate(BaseModel):
    id_pedido: int = Field(..., description="ID del pedido calificado")
    id_cliente: int = Field(..., description="ID del cliente que califica")
    fecha: Optional[str] = Field(None, description="Fecha ISO (si no se envía se usa la actual)")
    calificacion_servicio: int = Field(..., ge=1, le=5, description="Calificación del servicio (1-5)")
    comentario: str = Field(..., max_length=500, description="Opinión del cliente")
    productos: List[A_CalificacionProductoItem] = Field(..., min_length=1, description="Productos evaluados")


class A_CalificacionUpdate(BaseModel):
    calificacion_servicio: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=500)
    productos: Optional[List[A_CalificacionProductoItem]] = None


class A_CalificacionResponse(BaseModel):
    id: str
    id_pedido: int
    id_cliente: int
    fecha: str
    calificacion_servicio: int
    comentario: str
    productos: List[A_CalificacionProductoItem]


class A_CalificacionPromedioResponse(BaseModel):
    id_producto: int
    nombre_producto: Optional[str] = None
    promedio_calificacion: float
    total_evaluaciones: int
    calificaciones: List[A_CalificacionResponse]
