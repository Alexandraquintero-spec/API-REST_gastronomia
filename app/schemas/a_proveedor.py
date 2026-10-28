from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.a_comun import A_EstadoGeneral


class A_ProveedorBase(BaseModel):
    nit: str = Field(..., max_length=20, description="NIT o documento (único)")
    razon_social: str = Field(..., max_length=120, description="Nombre o razón social")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    correo: Optional[str] = Field(None, max_length=120, description="Correo de contacto")
    direccion: Optional[str] = Field(None, max_length=150, description="Dirección")
    estado: A_EstadoGeneral = Field("ACTIVO", description="Estado del proveedor")


class A_ProveedorCreate(A_ProveedorBase):
    pass


class A_ProveedorUpdate(BaseModel):
    nit: Optional[str] = Field(None, max_length=20)
    razon_social: Optional[str] = Field(None, max_length=120)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=120)
    direccion: Optional[str] = Field(None, max_length=150)
    estado: Optional[A_EstadoGeneral] = None


class A_ProveedorResponse(A_ProveedorBase):
    id_proveedor: int
    model_config = ConfigDict(from_attributes=True)
