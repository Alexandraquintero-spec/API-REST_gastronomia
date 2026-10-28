from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.a_comun import A_EstadoGeneral

A_TipoCliente = Literal["APRENDIZ", "INSTRUCTOR", "FUNCIONARIO", "EXTERNO"]


class A_ClienteBase(BaseModel):
    identificacion: str = Field(..., max_length=20, description="Documento de identidad (único)")
    nombres: str = Field(..., max_length=80, description="Nombres del cliente")
    apellidos: str = Field(..., max_length=80, description="Apellidos del cliente")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono")
    correo: Optional[str] = Field(None, max_length=120, description="Correo")
    tipo_cliente: A_TipoCliente = Field(..., description="Tipo de cliente")
    estado: A_EstadoGeneral = Field("ACTIVO", description="Estado del cliente")


class A_ClienteCreate(A_ClienteBase):
    pass


class A_ClienteUpdate(BaseModel):
    identificacion: Optional[str] = Field(None, max_length=20)
    nombres: Optional[str] = Field(None, max_length=80)
    apellidos: Optional[str] = Field(None, max_length=80)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=120)
    tipo_cliente: Optional[A_TipoCliente] = None
    estado: Optional[A_EstadoGeneral] = None


class A_ClienteResponse(A_ClienteBase):
    id_cliente: int
    model_config = ConfigDict(from_attributes=True)
