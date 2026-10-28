from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class A_RecetaBase(BaseModel):
    id_producto: int = Field(..., description="ID del producto")
    id_insumo: int = Field(..., description="ID del insumo")
    cantidad: float = Field(..., gt=0, description="Cantidad del insumo por unidad de producto")


class A_RecetaCreate(A_RecetaBase):
    pass


class A_RecetaUpdate(BaseModel):
    id_producto: Optional[int] = None
    id_insumo: Optional[int] = None
    cantidad: Optional[float] = Field(None, gt=0)


class A_RecetaResponse(A_RecetaBase):
    id_receta: int
    nombre_insumo: Optional[str] = None
    unidad_medida: Optional[str] = None
    costo_unitario: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)
