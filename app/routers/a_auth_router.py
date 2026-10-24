from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_LoginRequest,
    A_TokenResponse,
    A_UsuarioCreate,
    A_UsuarioResponse,
)
from app.controllers.a_controllers import a_autenticar_usuario, a_crear_usuario

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
    a_db: Database = Depends(a_get_db),
) -> A_TokenResponse:
    return a_autenticar_usuario(db=a_db, datos_login=a_datos_login)


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
    a_db: Database = Depends(a_get_db),
) -> A_UsuarioResponse:
    return a_crear_usuario(db=a_db, datos=a_datos)


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
