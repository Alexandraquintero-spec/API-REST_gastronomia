from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_auth import a_autenticar_usuario
from app.controllers.a_usuario import a_crear_usuario
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_auth import A_LoginRequest, A_PerfilResponse, A_TokenResponse
from app.schemas.a_usuario import A_UsuarioCreate, A_UsuarioResponse

a_router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@a_router.post(
    "/login",
    response_model=A_TokenResponse,
    summary="Iniciar sesión (único endpoint público)",
    description="Valida correo y contraseña y retorna el token JWT con el rol del usuario (RF01).",
    responses={401: {"description": "Credenciales inválidas"}, 403: {"description": "Usuario inactivo"}},
)
def a_login(a_datos: A_LoginRequest, a_db: Database = Depends(a_get_db)):
    return a_autenticar_usuario(a_db=a_db, a_datos_login=a_datos)


@a_router.post(
    "/registro",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario (solo ADMIN)",
    description="Crea un usuario con su rol. La contraseña se guarda cifrada con bcrypt (RN06).",
    responses={409: {"description": "Correo o documento ya registrado"}},
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)
def a_registro(a_datos: A_UsuarioCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_usuario(a_db=a_db, a_datos=a_datos)


@a_router.get(
    "/perfil",
    response_model=A_PerfilResponse,
    summary="Perfil del usuario autenticado",
    description="Retorna los datos del usuario contenidos en el token JWT.",
)
def a_perfil(a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual)):
    return a_usuario
