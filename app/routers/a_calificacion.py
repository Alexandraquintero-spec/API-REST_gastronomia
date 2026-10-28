from typing import List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_calificacion import (
    a_actualizar_calificacion,
    a_calificaciones_por_producto,
    a_crear_calificacion,
    a_eliminar_calificacion,
    a_listar_calificaciones,
    a_obtener_calificacion,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_calificacion import (
    A_CalificacionCreate,
    A_CalificacionPromedioResponse,
    A_CalificacionResponse,
    A_CalificacionUpdate,
)
from app.schemas.a_comun import A_MensajeResponse

a_router = APIRouter(
    prefix="/api/v1/calificaciones",
    tags=["Calificaciones"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "CAJERO"]))],
)


@a_router.get("", response_model=List[A_CalificacionResponse], summary="Listar calificaciones")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_calificaciones(a_db=a_db)


@a_router.get(
    "/producto/{id_producto}",
    response_model=A_CalificacionPromedioResponse,
    summary="Calificaciones y promedio de un producto",
)
def a_por_producto(id_producto: int, a_db: Database = Depends(a_get_db)):
    return a_calificaciones_por_producto(a_db=a_db, a_id_producto=id_producto)


@a_router.get(
    "/{id}",
    response_model=A_CalificacionResponse,
    summary="Obtener calificación por ID",
    description="El ID es el ObjectId de MongoDB (24 caracteres hexadecimales).",
    responses={400: {"description": "ID inválido"}, 404: {"description": "Calificación no encontrada"}},
)
def a_obtener(id: str, a_db: Database = Depends(a_get_db)):
    return a_obtener_calificacion(a_db=a_db, a_id_calificacion=id)


@a_router.post(
    "",
    response_model=A_CalificacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar calificación",
    description="El pedido debe pertenecer al cliente y los productos deben estar en el pedido. Un pedido se califica una vez.",
    responses={
        400: {"description": "Pedido de otro cliente o productos ajenos al pedido"},
        404: {"description": "Pedido o cliente no existe"},
        409: {"description": "El pedido ya fue calificado"},
    },
)
def a_crear(a_datos: A_CalificacionCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_calificacion(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_CalificacionResponse,
    summary="Actualizar calificación",
    responses={400: {"description": "ID inválido"}, 404: {"description": "Calificación no encontrada"}},
)
def a_actualizar(id: str, a_datos: A_CalificacionUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_calificacion(a_db=a_db, a_id_calificacion=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar calificación",
    responses={400: {"description": "ID inválido"}, 404: {"description": "Calificación no encontrada"}},
)
def a_eliminar(id: str, a_db: Database = Depends(a_get_db)):
    return a_eliminar_calificacion(a_db=a_db, a_id_calificacion=id)
