from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import A_InsumoCreate, A_InsumoResponse, A_InsumoUpdate
from app.controllers.a_controllers import (
    a_actualizar_insumo,
    a_crear_insumo,
    a_eliminar_insumo,
    a_insumos_por_vencer,
    a_insumos_stock_bajo,
    a_listar_insumos,
    a_obtener_insumo,
)

a_insumos_router = APIRouter(
    prefix="/insumos",
    tags=["Insumos"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "COCINERO"]))],
)


@a_insumos_router.get(
    "",
    response_model=List[A_InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar insumos",
    description="Retorna el listado completo de insumos e ingredientes del inventario (ADMIN, COCINERO).",
)
def a_listar_insumos_route(
    a_db: Database = Depends(a_get_db),
) -> List[A_InsumoResponse]:
    return a_listar_insumos(db=a_db)


@a_insumos_router.get(
    "/stock-bajo",
    response_model=List[A_InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar insumos con stock bajo",
    description="Filtra insumos cuyo stock_actual sea menor o igual al stock_minimo (RF07).",
)
def a_insumos_stock_bajo_route(
    a_db: Database = Depends(a_get_db),
) -> List[A_InsumoResponse]:
    return a_insumos_stock_bajo(db=a_db)


@a_insumos_router.get(
    "/por-vencer",
    response_model=List[A_InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar insumos próximos a vencer",
    description="Retorna los insumos que vencen en los próximos N días (por defecto 7 días) (RF07).",
)
def a_insumos_por_vencer_route(
    dias: int = Query(7, ge=1, description="Número de días hacia adelante para verificar vencimiento"),
    a_db: Database = Depends(a_get_db),
) -> List[A_InsumoResponse]:
    return a_insumos_por_vencer(db=a_db, dias=dias)


@a_insumos_router.get(
    "/{id}",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener insumo por ID",
    description="Retorna la información detallada de un insumo específico por su ID.",
)
def a_obtener_insumo_route(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> A_InsumoResponse:
    return a_obtener_insumo(db=a_db, id_insumo=id)


@a_insumos_router.post(
    "",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear insumo",
    description="Registra un nuevo insumo en el inventario con su stock y unidad de medida.",
)
def a_crear_insumo_route(
    a_datos: A_InsumoCreate,
    a_db: Database = Depends(a_get_db),
) -> A_InsumoResponse:
    return a_crear_insumo(db=a_db, datos=a_datos)


@a_insumos_router.put(
    "/{id}",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar insumo",
    description="Actualiza la información de un insumo existente.",
)
def a_actualizar_insumo_route(
    id: int,
    a_datos: A_InsumoUpdate,
    a_db: Database = Depends(a_get_db),
) -> A_InsumoResponse:
    return a_actualizar_insumo(db=a_db, id_insumo=id, datos=a_datos)


@a_insumos_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar insumo",
    description="Elimina un insumo. Si tiene recetas o compras asociadas, se cambia a estado INACTIVO según la RN04.",
)
def a_eliminar_insumo_route(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_eliminar_insumo(db=a_db, id_insumo=id)
