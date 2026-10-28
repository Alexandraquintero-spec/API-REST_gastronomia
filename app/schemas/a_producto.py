from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.a_receta import A_RecetaResponse

A_EstadoProducto = Literal["DISPONIBLE", "AGOTADO", "INACTIVO"]


class A_ProductoBase(BaseModel):
    codigo: str = Field(..., max_length=20, description="Código interno (único)")
    nombre: str = Field(..., max_length=100, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio_venta: float = Field(..., gt=0, description="Precio de venta (> 0)")
    unidad_venta: str = Field(..., max_length=20, description="Porción, unidad, vaso, libra...")
    id_categoria: int = Field(..., description="ID de la categoría")
    estado: A_EstadoProducto = Field("DISPONIBLE", description="Estado")


class A_ProductoCreate(A_ProductoBase):
    pass


class A_ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    precio_venta: Optional[float] = Field(None, gt=0)
    unidad_venta: Optional[str] = Field(None, max_length=20)
    id_categoria: Optional[int] = None
    estado: Optional[A_EstadoProducto] = None


class A_ProductoResponse(A_ProductoBase):
    id_producto: int
    model_config = ConfigDict(from_attributes=True)


class A_ProductoCostoResponse(BaseModel):
    """Costo de producción y margen de ganancia (RF06)."""
    id_producto: int
    codigo: str
    nombre: str
    precio_venta: float
    costo_produccion: float
    margen_ganancia: float
    porcentaje_margen: float
    receta: List[A_RecetaResponse]
