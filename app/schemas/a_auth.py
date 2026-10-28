from pydantic import BaseModel, EmailStr, Field


class A_LoginRequest(BaseModel):
    """Datos de inicio de sesión."""
    correo: EmailStr = Field(..., description="Correo de acceso", examples=["admin@gastronomia.sena.edu.co"])
    password: str = Field(..., min_length=4, description="Contraseña de acceso", examples=["Admin123*"])


class A_TokenResponse(BaseModel):
    """Respuesta con token JWT y datos de sesión."""
    access_token: str
    token_type: str = "bearer"
    rol: str
    id_usuario: int
    nombres: str


class A_PerfilResponse(BaseModel):
    """Datos del usuario autenticado tomados del token."""
    id_usuario: int
    correo: str
    rol: str
    nombres: str
