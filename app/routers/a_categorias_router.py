from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_CategoriaCreate,
    A_CategoriaResponse,
    A_CategoriaUpdate,
)
from app.controllers.a_controllers import (
    a_actualizar_categoria,
    a_crear_categoria,
    a_eliminar_categoria,
    a_listar_categorias,
    a_obtener_categoria,
)

a_categorias_router = APIRouter(prefix="/categorias", tags=["Categorías"])


@a_categorias_router.get(
    "",
    response_model=List[A_CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
    description="Obtiene todas las categorías de productos (disponible para todos los usuarios autenticados).",
)
def a_listar_categorias_route(
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Database = Depends(a_get_db),
) -> List[A_CategoriaResponse]:
    return a_listar_categorias(db=a_db)


@a_categorias_router.get(
    "/{id}",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener categoría por ID",
    description="Obtiene la información de una categoría específica por ID.",
)
def a_obtener_categoria_route(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Database = Depends(a_get_db),
) -> A_CategoriaResponse:
    return a_obtener_categoria(db=a_db, id_categoria=id)


@a_categorias_router.post(
    "",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="Crea una nueva categoría de productos (solo ADMIN).",
)
def a_crear_categoria_route(
    a_datos: A_CategoriaCreate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> A_CategoriaResponse:
    return a_crear_categoria(db=a_db, datos=a_datos)


@a_categorias_router.put(
    "/{id}",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría",
    description="Actualiza una categoría existente (solo ADMIN).",
)
def a_actualizar_categoria_route(
    id: int,
    a_datos: A_CategoriaUpdate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> A_CategoriaResponse:
    return a_actualizar_categoria(db=a_db, id_categoria=id, datos=a_datos)


@a_categorias_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar categoría",
    description="Elimina una categoría del sistema si no contiene productos (solo ADMIN).",
)
def a_eliminar_categoria_route(
    id: int,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_eliminar_categoria(db=a_db, id_categoria=id)
