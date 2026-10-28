from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.a_comun import A_EstadoGeneral

A_Rol = Literal["ADMIN", "CAJERO", "COCINERO"]


class A_UsuarioBase(BaseModel):
    identificacion: str = Field(..., max_length=20, description="Documento de identidad único")
    nombres: str = Field(..., max_length=80, description="Nombres del usuario")
    apellidos: str = Field(..., max_length=80, description="Apellidos del usuario")
    correo: EmailStr = Field(..., description="Correo de acceso (único)")
    rol: A_Rol = Field(..., description="Rol del usuario en el sistema")
    estado: A_EstadoGeneral = Field("ACTIVO", description="Estado del usuario")


class A_UsuarioCreate(A_UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña en texto plano (se cifra con bcrypt)")


class A_UsuarioUpdate(BaseModel):
    identificacion: Optional[str] = Field(None, max_length=20)
    nombres: Optional[str] = Field(None, max_length=80)
    apellidos: Optional[str] = Field(None, max_length=80)
    correo: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    rol: Optional[A_Rol] = None
    estado: Optional[A_EstadoGeneral] = None


class A_UsuarioResponse(A_UsuarioBase):
    """Respuesta sin el campo password (RN06)."""
    id_usuario: int
    model_config = ConfigDict(from_attributes=True)
