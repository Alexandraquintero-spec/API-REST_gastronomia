from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import A_UsuarioCreate, A_UsuarioResponse, A_UsuarioUpdate
from app.controllers.a_controllers import (
    a_actualizar_usuario,
    a_crear_usuario,
    a_eliminar_usuario,
    a_listar_usuarios,
    a_obtener_usuario,
)

a_usuarios_router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_usuarios_router.get(
    "",
    response_model=List[A_UsuarioResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Obtiene el listado completo de usuarios del sistema (solo ADMIN).",
)
def a_listar_usuarios_route(
    a_db: Database = Depends(a_get_db),
) -> List[A_UsuarioResponse]:
    return a_listar_usuarios(db=a_db)


@a_usuarios_router.get(
    "/{id}",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Obtiene el detalle de un usuario específico por su identificador numérico (solo ADMIN).",
)
def a_obtener_usuario_route(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> A_UsuarioResponse:
    return a_obtener_usuario(db=a_db, id_usuario=id)


@a_usuarios_router.post(
    "",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en la base de datos con contraseña cifrada en bcrypt (RN06) (solo ADMIN).",
)
def a_crear_usuario_route(
    a_datos: A_UsuarioCreate,
    a_db: Database = Depends(a_get_db),
) -> A_UsuarioResponse:
    return a_crear_usuario(db=a_db, datos=a_datos)


@a_usuarios_router.put(
    "/{id}",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
    description="Actualiza la información de un usuario existente (solo ADMIN).",
)
def a_actualizar_usuario_route(
    id: int,
    a_datos: A_UsuarioUpdate,
    a_db: Database = Depends(a_get_db),
) -> A_UsuarioResponse:
    return a_actualizar_usuario(db=a_db, id_usuario=id, datos=a_datos)


@a_usuarios_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario",
    description="Elimina un usuario del sistema por su identificador (solo ADMIN).",
)
def a_eliminar_usuario_route(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_eliminar_usuario(db=a_db, id_usuario=id)
