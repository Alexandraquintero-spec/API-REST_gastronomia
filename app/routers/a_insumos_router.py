from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.a_security import a_requerir_roles
from app.database.a_conexion_mysql import a_obtener_db_mysql
from app.schemas.a_schemas import A_InsumoCreate, A_InsumoResponse, A_InsumoUpdate
from app.services.a_services import A_InsumoService

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
    responses={
        200: {"description": "Lista de insumos"},
        403: {"description": "Rol no autorizado"},
    },
)
def a_listar_insumos(
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_InsumoResponse]:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_listar_insumos()


@a_insumos_router.get(
    "/stock-bajo",
    response_model=List[A_InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar insumos con stock bajo",
    description="Filtra insumos cuyo stock_actual sea menor o igual al stock_minimo (RF07).",
    responses={
        200: {"description": "Lista de insumos con alerta de existencias"},
    },
)
def a_insumos_stock_bajo(
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_InsumoResponse]:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_listar_stock_bajo()


@a_insumos_router.get(
    "/por-vencer",
    response_model=List[A_InsumoResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar insumos próximos a vencer",
    description="Retorna los insumos que vencen en los próximos N días (por defecto 7 días) (RF07).",
    responses={
        200: {"description": "Lista de insumos próximos a vencer"},
    },
)
def a_insumos_por_vencer(
    dias: int = Query(7, ge=1, description="Número de días hacia adelante para verificar vencimiento"),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_InsumoResponse]:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_listar_por_vencer(dias)


@a_insumos_router.get(
    "/{id}",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener insumo por ID",
    description="Retorna la información detallada de un insumo específico por su ID.",
    responses={
        200: {"description": "Insumo encontrado"},
        404: {"description": "Insumo no encontrado"},
    },
)
def a_obtener_insumo(
    id: int,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_InsumoResponse:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_obtener_por_id(id)


@a_insumos_router.post(
    "",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear insumo",
    description="Registra un nuevo insumo en el inventario con su stock y unidad de medida.",
    responses={
        201: {"description": "Insumo creado"},
        409: {"description": "Nombre de insumo ya existe"},
    },
)
def a_crear_insumo(
    a_datos: A_InsumoCreate,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_InsumoResponse:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_crear_insumo(a_datos)


@a_insumos_router.put(
    "/{id}",
    response_model=A_InsumoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar insumo",
    description="Actualiza la información de un insumo existente.",
    responses={
        200: {"description": "Insumo actualizado"},
        404: {"description": "Insumo no encontrado"},
        409: {"description": "Nombre duplicado"},
    },
)
def a_actualizar_insumo(
    id: int,
    a_datos: A_InsumoUpdate,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_InsumoResponse:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_actualizar_insumo(id, a_datos)


@a_insumos_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar insumo",
    description="Elimina un insumo. Si tiene recetas o compras asociadas, se cambia a estado INACTIVO según la RN04.",
    responses={
        200: {"description": "Insumo eliminado o inactivado según movimientos"},
        404: {"description": "Insumo no encontrado"},
    },
)
def a_eliminar_insumo(
    id: int,
    a_db: Session = Depends(a_obtener_db_mysql),
) -> Dict[str, str]:
    a_servicio = A_InsumoService(a_db)
    return a_servicio.a_eliminar_insumo(id)
