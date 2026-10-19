from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_conexion_mysql import a_obtener_db_mysql
from app.schemas.a_schemas import (
    A_CategoriaCreate,
    A_CategoriaResponse,
    A_CategoriaUpdate,
)
from app.services.a_services import A_CategoriaService

a_categorias_router = APIRouter(prefix="/categorias", tags=["Categorías"])


@a_categorias_router.get(
    "",
    response_model=List[A_CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
    description="Obtiene todas las categorías de productos (disponible para todos los usuarios autenticados).",
    responses={
        200: {"description": "Lista de categorías"},
        401: {"description": "Token inválido o ausente"},
    },
)
def a_listar_categorias(
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_CategoriaResponse]:
    a_servicio = A_CategoriaService(a_db)
    return a_servicio.a_listar_categorias()


@a_categorias_router.get(
    "/{id}",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener categoría por ID",
    description="Obtiene la información de una categoría específica por ID.",
    responses={
        200: {"description": "Categoría encontrada"},
        404: {"description": "Categoría no encontrada"},
    },
)
def a_obtener_categoria(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_CategoriaResponse:
    a_servicio = A_CategoriaService(a_db)
    return a_servicio.a_obtener_por_id(id)


@a_categorias_router.post(
    "",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="Crea una nueva categoría de productos (solo ADMIN).",
    responses={
        201: {"description": "Categoría creada"},
        403: {"description": "Permisos insuficientes"},
        409: {"description": "Ya existe una categoría con ese nombre"},
    },
)
def a_crear_categoria(
    a_datos: A_CategoriaCreate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_CategoriaResponse:
    a_servicio = A_CategoriaService(a_db)
    return a_servicio.a_crear_categoria(a_datos)


@a_categorias_router.put(
    "/{id}",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría",
    description="Actualiza una categoría existente (solo ADMIN).",
    responses={
        200: {"description": "Categoría actualizada"},
        404: {"description": "Categoría no encontrada"},
        409: {"description": "Nombre duplicado"},
    },
)
def a_actualizar_categoria(
    id: int,
    a_datos: A_CategoriaUpdate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_CategoriaResponse:
    a_servicio = A_CategoriaService(a_db)
    return a_servicio.a_actualizar_categoria(id, a_datos)


@a_categorias_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar categoría",
    description="Elimina una categoría del sistema si no contiene productos (solo ADMIN).",
    responses={
        200: {"description": "Categoría eliminada"},
        404: {"description": "Categoría no encontrada"},
        409: {"description": "La categoría tiene productos asociados"},
    },
)
def a_eliminar_categoria(
    id: int,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> Dict[str, str]:
    a_servicio = A_CategoriaService(a_db)
    return a_servicio.a_eliminar_categoria(id)
