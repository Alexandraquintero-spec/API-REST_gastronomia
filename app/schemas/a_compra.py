from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class A_DetalleCompraCreate(BaseModel):
    id_insumo: int = Field(..., description="ID del insumo comprado")
    cantidad: float = Field(..., gt=0, description="Cantidad comprada")
    costo_unitario: float = Field(..., ge=0, description="Nuevo costo unitario del insumo")


class A_CompraCreate(BaseModel):
    numero_factura: str = Field(..., max_length=30, description="Factura del proveedor")
    id_proveedor: int = Field(..., description="ID del proveedor")
    detalles: List[A_DetalleCompraCreate] = Field(..., min_length=1, description="Ítems de la compra")


class A_CompraUpdate(BaseModel):
    """Solo se permite corregir la factura; los ítems ya afectaron el inventario (RN02)."""
    numero_factura: str = Field(..., max_length=30, description="Número de factura corregido")


class A_DetalleCompraResponse(BaseModel):
    id_detalle_compra: Optional[int] = None
    id_insumo: int
    nombre_insumo: Optional[str] = None
    cantidad: float
    costo_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class A_CompraResponse(BaseModel):
    id_compra: int
    numero_factura: str
    fecha_compra: str
    id_proveedor: int
    id_usuario: int
    total: float
    detalles: List[A_DetalleCompraResponse] = []
    model_config = ConfigDict(from_attributes=True)
