from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.a_security import a_requerir_roles
from app.database.a_conexion_mysql import a_obtener_db_mysql
from app.schemas.a_schemas import A_UsuarioCreate, A_UsuarioResponse, A_UsuarioUpdate
from app.services.a_services import A_UsuarioService

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
    responses={
        200: {"description": "Lista de usuarios"},
        401: {"description": "Token inválido o ausente"},
        403: {"description": "Rol no autorizado"},
    },
)
def a_listar_usuarios(
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_UsuarioResponse]:
    a_servicio = A_UsuarioService(a_db)
    return a_servicio.a_listar_usuarios()


@a_usuarios_router.get(
    "/{id}",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Obtiene el detalle de un usuario específico por su identificador numérico (solo ADMIN).",
    responses={
        200: {"description": "Usuario encontrado"},
        404: {"description": "Usuario no encontrado"},
    },
)
def a_obtener_usuario(
    id: int,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_UsuarioResponse:
    a_servicio = A_UsuarioService(a_db)
    return a_servicio.a_obtener_por_id(id)


@a_usuarios_router.post(
    "",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en la base de datos con contraseña cifrada en bcrypt (RN06) (solo ADMIN).",
    responses={
        201: {"description": "Usuario creado"},
        409: {"description": "Correo o identificación duplicados"},
    },
)
def a_crear_usuario(
    a_datos: A_UsuarioCreate,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_UsuarioResponse:
    a_servicio = A_UsuarioService(a_db)
    return a_servicio.a_crear_usuario(a_datos)


@a_usuarios_router.put(
    "/{id}",
    response_model=A_UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
    description="Actualiza la información de un usuario existente (solo ADMIN).",
    responses={
        200: {"description": "Usuario actualizado"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "Conflicto por datos duplicados"},
    },
)
def a_actualizar_usuario(
    id: int,
    a_datos: A_UsuarioUpdate,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_UsuarioResponse:
    a_servicio = A_UsuarioService(a_db)
    return a_servicio.a_actualizar_usuario(id, a_datos)


@a_usuarios_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario",
    description="Elimina un usuario del sistema por su identificador (solo ADMIN).",
    responses={
        200: {"description": "Usuario eliminado"},
        404: {"description": "Usuario no encontrado"},
    },
)
def a_eliminar_usuario(
    id: int,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> Dict[str, str]:
    a_servicio = A_UsuarioService(a_db)
    return a_servicio.a_eliminar_usuario(id)
