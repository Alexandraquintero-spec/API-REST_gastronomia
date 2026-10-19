from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_conexion_mysql import a_obtener_db_mysql
from app.schemas.a_schemas import (
    A_LoginRequest,
    A_TokenResponse,
    A_UsuarioCreate,
    A_UsuarioResponse,
)
from app.services.a_services import A_AuthService, A_UsuarioService

a_auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])


@a_auth_router.post(
    "/login",
    response_model=A_TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica usuario con correo y contraseña, y retorna el token JWT con su rol (RF01). Único endpoint público.",
    responses={
        200: {"description": "Inicio de sesión exitoso con token JWT"},
        401: {"description": "Credenciales inválidas"},
        403: {"description": "Usuario inactivo en el sistema"},
    },
)
def a_login(
    a_datos_login: A_LoginRequest,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_TokenResponse:
    a_servicio = A_AuthService(a_db)
    return a_servicio.a_autenticar_usuario(a_datos_login)


@a_auth_router.post(
    "/registro",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario nuevo",
    description="Permite registrar un nuevo usuario con rol asignado. Solo permitido para administradores (ADMIN).",
    responses={
        201: {"description": "Usuario registrado exitosamente"},
        401: {"description": "No autorizado por falta o invalidez de token"},
        403: {"description": "Permisos insuficientes (requiere rol ADMIN)"},
        409: {"description": "El correo o documento ya existe"},
    },
)
def a_registro(
    a_datos: A_UsuarioCreate,
    a_usuario_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_UsuarioResponse:
    a_servicio = A_UsuarioService(a_db)
    return a_servicio.a_crear_usuario(a_datos)


@a_auth_router.get(
    "/perfil",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Consultar perfil del usuario autenticado",
    description="Retorna la información del usuario en sesión a partir de los claims del token JWT verificado.",
    responses={
        200: {"description": "Datos del perfil autenticado"},
        401: {"description": "Token ausente o inválido"},
    },
)
def a_perfil(
    a_usuario_actual: Dict[str, Any] = Depends(a_obtener_usuario_actual),
) -> Dict[str, Any]:
    return a_usuario_actual
