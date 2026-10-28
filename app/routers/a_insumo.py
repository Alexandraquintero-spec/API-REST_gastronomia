from typing import List
from fastapi import APIRouter, Depends, Query, status
from pymongo.database import Database
from app.controllers.a_insumo import (
    a_actualizar_insumo,
    a_crear_insumo,
    a_eliminar_insumo,
    a_insumos_por_vencer,
    a_insumos_stock_bajo,
    a_listar_insumos,
    a_obtener_insumo,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_insumo import A_InsumoCreate, A_InsumoResponse, A_InsumoUpdate

a_router = APIRouter(
    prefix="/api/v1/insumos",
    tags=["Insumos"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "COCINERO"]))],
)


@a_router.get("", response_model=List[A_InsumoResponse], summary="Listar insumos")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_insumos(a_db=a_db)


@a_router.get(
    "/stock-bajo",
    response_model=List[A_InsumoResponse],
    summary="Insumos con stock bajo",
    description="Insumos con stock_actual <= stock_minimo (RF07).",
)
def a_stock_bajo(a_db: Database = Depends(a_get_db)):
    return a_insumos_stock_bajo(a_db=a_db)


@a_router.get(
    "/por-vencer",
    response_model=List[A_InsumoResponse],
    summary="Insumos próximos a vencer",
    description="Insumos que vencen entre hoy y los próximos N días (RF07).",
)
def a_por_vencer(
    dias: int = Query(7, ge=1, le=365, description="Días hacia adelante"),
    a_db: Database = Depends(a_get_db),
):
    return a_insumos_por_vencer(a_db=a_db, a_dias=dias)


@a_router.get(
    "/{id}",
    response_model=A_InsumoResponse,
    summary="Obtener insumo por ID",
    responses={404: {"description": "Insumo no encontrado"}},
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_insumo(a_db=a_db, a_id_insumo=id)


@a_router.post(
    "",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear insumo",
    responses={409: {"description": "Nombre duplicado"}},
)
def a_crear(a_datos: A_InsumoCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_insumo(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_InsumoResponse,
    summary="Actualizar insumo",
    responses={404: {"description": "Insumo no encontrado"}, 409: {"description": "Nombre duplicado"}},
)
def a_actualizar(id: int, a_datos: A_InsumoUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_insumo(a_db=a_db, a_id_insumo=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar insumo",
    description="RN04: si está en recetas o compras se cambia a INACTIVO (borrado lógico).",
    responses={404: {"description": "Insumo no encontrado"}},
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_insumo(a_db=a_db, a_id_insumo=id)
