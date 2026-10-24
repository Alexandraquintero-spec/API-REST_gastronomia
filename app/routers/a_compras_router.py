from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import A_CompraCreate, A_CompraResponse
from app.controllers import a_controllers

a_compras_router = APIRouter(
    prefix="/compras",
    tags=["Compras"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_compras_router.get(
    "",
    response_model=List[A_CompraResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar compras",
    description="Retorna el historial completo de compras registradas en el sistema (solo ADMIN).",
    responses={
        200: {"description": "Lista de compras"},
    },
)
def a_listar_compras(
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_listar_compras(a_db)


@a_compras_router.get(
    "/{id}",
    response_model=A_CompraResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener compra por ID",
    description="Retorna el detalle completo de una compra y sus insumos adquiridos.",
    responses={
        200: {"description": "Compra encontrada"},
        404: {"description": "Compra no encontrada"},
    },
)
def a_obtener_compra(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_obtener_compra(a_db, id)


@a_compras_router.post(
    "",
    response_model=A_CompraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar compra de insumos",
    description="Registra una nueva compra con sus ítems, incrementando el stock_actual y actualizando el costo_unitario de cada insumo (RN02).",
    responses={
        201: {"description": "Compra registrada exitosamente"},
        404: {"description": "Insumo o proveedor no encontrado"},
    },
)
def a_crear_compra(
    a_datos: A_CompraCreate,
    a_usuario_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    a_id_usuario = a_usuario_admin.get("id_usuario", 1)
    return a_controllers.a_crear_compra(a_db, a_datos, a_id_usuario)


@a_compras_router.put(
    "/{id}",
    response_model=A_CompraResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar compra",
    description="Actualiza datos de cabecera de la factura de compra.",
    responses={
        200: {"description": "Compra actualizada"},
        404: {"description": "Compra no encontrada"},
    },
)
def a_actualizar_compra(
    id: int,
    a_datos: Dict[str, Any],
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_actualizar_compra(a_db, id, a_datos)


@a_compras_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar compra",
    description="Elimina una compra del sistema por su identificador.",
    responses={
        200: {"description": "Compra eliminada"},
        404: {"description": "Compra no encontrada"},
    },
)
def a_eliminar_compra(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_controllers.a_eliminar_compra(a_db, id)
