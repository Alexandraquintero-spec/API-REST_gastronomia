from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_CalificacionCreate,
    A_CalificacionPromedioProductoResponse,
    A_CalificacionResponse,
    A_CalificacionUpdate,
)
from app.controllers import a_controllers

a_calificaciones_router = APIRouter(
    prefix="/calificaciones",
    tags=["Calificaciones (MongoDB)"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "CAJERO"]))],
)


@a_calificaciones_router.get(
    "",
    response_model=List[A_CalificacionResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar calificaciones",
    description="Obtiene todas las calificaciones registradas en MongoDB (ADMIN, CAJERO).",
    responses={
        200: {"description": "Lista de calificaciones"},
    },
)
def a_listar_calificaciones(
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_listar_calificaciones(a_db)


@a_calificaciones_router.get(
    "/producto/{id_producto}",
    response_model=A_CalificacionPromedioProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Calificaciones y promedio de un producto",
    description="Consulta todas las calificaciones recibidas por un producto en MongoDB y calcula su calificación promedio ponderada (RF12).",
    responses={
        200: {"description": "Calificaciones y promedio del producto"},
    },
)
def a_calificaciones_por_producto(
    id_producto: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_calificaciones_por_producto(a_db, id_producto)


@a_calificaciones_router.get(
    "/{id}",
    response_model=A_CalificacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener calificación por ID",
    description="Retorna el documento de calificación de MongoDB por su ID.",
    responses={
        200: {"description": "Calificación encontrada"},
        404: {"description": "Calificación no encontrada"},
    },
)
def a_obtener_calificacion(
    id: str,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_obtener_calificacion(a_db, id)


@a_calificaciones_router.post(
    "",
    response_model=A_CalificacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar calificación",
    description="Almacena una nueva calificación del cliente en MongoDB, validada según el esquema $jsonSchema (RF12).",
    responses={
        201: {"description": "Calificación registrada"},
        404: {"description": "Pedido o cliente no existe"},
        409: {"description": "El pedido ya fue calificado"},
    },
)
def a_crear_calificacion(
    a_datos: A_CalificacionCreate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_crear_calificacion(a_db, a_datos)


@a_calificaciones_router.put(
    "/{id}",
    response_model=A_CalificacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar calificación",
    description="Actualiza el comentario o las puntuaciones de un documento en MongoDB.",
    responses={
        200: {"description": "Calificación actualizada"},
        404: {"description": "Calificación no encontrada"},
    },
)
def a_actualizar_calificacion(
    id: str,
    a_datos: A_CalificacionUpdate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_actualizar_calificacion(a_db, id, a_datos)


@a_calificaciones_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar calificación",
    description="Elimina una calificación de MongoDB por su identificador.",
    responses={
        200: {"description": "Calificación eliminada"},
        404: {"description": "Calificación no encontrada"},
    },
)
def a_eliminar_calificacion(
    id: str,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_controllers.a_eliminar_calificacion(a_db, id)
