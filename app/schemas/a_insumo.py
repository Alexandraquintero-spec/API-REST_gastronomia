from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.a_comun import A_EstadoGeneral, A_PATRON_FECHA

A_UnidadMedida = Literal["g", "kg", "ml", "l", "lb", "unidad"]


class A_InsumoBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre único del insumo")
    unidad_medida: A_UnidadMedida = Field(..., description="Unidad de medida")
    stock_actual: float = Field(0.0, ge=0, description="Existencias actuales")
    stock_minimo: float = Field(0.0, ge=0, description="Nivel mínimo de alerta")
    costo_unitario: float = Field(0.0, ge=0, description="Costo por unidad de medida")
    fecha_vencimiento: Optional[str] = Field(
        None, pattern=A_PATRON_FECHA, description="Vencimiento del lote (YYYY-MM-DD)"
    )
    estado: A_EstadoGeneral = Field("ACTIVO", description="Estado")


class A_InsumoCreate(A_InsumoBase):
    pass


class A_InsumoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    unidad_medida: Optional[A_UnidadMedida] = None
    stock_actual: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[float] = Field(None, ge=0)
    costo_unitario: Optional[float] = Field(None, ge=0)
    fecha_vencimiento: Optional[str] = Field(None, pattern=A_PATRON_FECHA)
    estado: Optional[A_EstadoGeneral] = None


class A_InsumoResponse(A_InsumoBase):
    id_insumo: int
    model_config = ConfigDict(from_attributes=True)
