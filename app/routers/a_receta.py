from typing import List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_receta import (
    a_actualizar_receta,
    a_crear_receta,
    a_eliminar_receta,
    a_listar_recetas,
    a_obtener_receta,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_receta import A_RecetaCreate, A_RecetaResponse, A_RecetaUpdate

a_router = APIRouter(
    prefix="/api/v1/recetas",
    tags=["Recetas"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "COCINERO"]))],
)


@a_router.get("", response_model=List[A_RecetaResponse], summary="Listar ítems de receta")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_recetas(a_db=a_db)


@a_router.get(
    "/{id}",
    response_model=A_RecetaResponse,
    summary="Obtener ítem de receta por ID",
    responses={404: {"description": "Receta no encontrada"}},
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_receta(a_db=a_db, a_id_receta=id)


@a_router.post(
    "",
    response_model=A_RecetaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar insumo a la receta de un producto",
    responses={404: {"description": "Producto o insumo no existe"}, 409: {"description": "Insumo ya está en la receta"}},
)
def a_crear(a_datos: A_RecetaCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_receta(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_RecetaResponse,
    summary="Actualizar ítem de receta",
    responses={404: {"description": "Receta, producto o insumo no encontrado"}},
)
def a_actualizar(id: int, a_datos: A_RecetaUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_receta(a_db=a_db, a_id_receta=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar ítem de receta",
    responses={404: {"description": "Receta no encontrada"}},
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_receta(a_db=a_db, a_id_receta=id)
