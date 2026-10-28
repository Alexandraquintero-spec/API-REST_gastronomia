from typing import List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_categoria import (
    a_actualizar_categoria,
    a_crear_categoria,
    a_eliminar_categoria,
    a_listar_categorias,
    a_obtener_categoria,
)
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_categoria import A_CategoriaCreate, A_CategoriaResponse, A_CategoriaUpdate
from app.schemas.a_comun import A_MensajeResponse

# Consulta: cualquier usuario autenticado. Escritura: solo ADMIN.
a_router = APIRouter(prefix="/api/v1/categorias", tags=["Categorías"])
a_solo_admin = [Depends(a_requerir_roles(["ADMIN"]))]
a_autenticado = [Depends(a_obtener_usuario_actual)]


@a_router.get("", response_model=List[A_CategoriaResponse], summary="Listar categorías", dependencies=a_autenticado)
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_categorias(a_db=a_db)


@a_router.get(
    "/{id}",
    response_model=A_CategoriaResponse,
    summary="Obtener categoría por ID",
    responses={404: {"description": "Categoría no encontrada"}},
    dependencies=a_autenticado,
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_categoria(a_db=a_db, a_id_categoria=id)


@a_router.post(
    "",
    response_model=A_CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría (ADMIN)",
    responses={409: {"description": "Nombre duplicado"}},
    dependencies=a_solo_admin,
)
def a_crear(a_datos: A_CategoriaCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_categoria(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_CategoriaResponse,
    summary="Actualizar categoría (ADMIN)",
    responses={404: {"description": "Categoría no encontrada"}, 409: {"description": "Nombre duplicado"}},
    dependencies=a_solo_admin,
)
def a_actualizar(id: int, a_datos: A_CategoriaUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_categoria(a_db=a_db, a_id_categoria=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar categoría (ADMIN)",
    description="Si tiene productos asociados se inactiva (borrado lógico).",
    responses={404: {"description": "Categoría no encontrada"}},
    dependencies=a_solo_admin,
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_categoria(a_db=a_db, a_id_categoria=id)
