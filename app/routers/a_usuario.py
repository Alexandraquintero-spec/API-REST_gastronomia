from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_usuario import (
    a_actualizar_usuario,
    a_crear_usuario,
    a_eliminar_usuario,
    a_listar_usuarios,
    a_obtener_usuario,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_usuario import A_UsuarioCreate, A_UsuarioResponse, A_UsuarioUpdate

# Recurso exclusivo del rol ADMIN
a_router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_router.get("", response_model=List[A_UsuarioResponse], summary="Listar usuarios")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_usuarios(a_db=a_db)


@a_router.get(
    "/{id}",
    response_model=A_UsuarioResponse,
    summary="Obtener usuario por ID",
    responses={404: {"description": "Usuario no encontrado"}},
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_usuario(a_db=a_db, a_id_usuario=id)


@a_router.post(
    "",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="La contraseña se cifra con bcrypt y nunca se devuelve (RN06).",
    responses={409: {"description": "Correo o documento ya registrado"}},
)
def a_crear(a_datos: A_UsuarioCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_usuario(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_UsuarioResponse,
    summary="Actualizar usuario",
    description="Solo se modifican los campos enviados.",
    responses={404: {"description": "Usuario no encontrado"}, 409: {"description": "Correo o documento duplicado"}},
)
def a_actualizar(id: int, a_datos: A_UsuarioUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_usuario(a_db=a_db, a_id_usuario=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar usuario",
    responses={404: {"description": "Usuario no encontrado"}, 409: {"description": "No puede eliminarse a sí mismo"}},
)
def a_eliminar(
    id: int,
    a_db: Database = Depends(a_get_db),
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
):
    return a_eliminar_usuario(a_db=a_db, a_id_usuario=id, a_id_usuario_actual=a_usuario["id_usuario"])
