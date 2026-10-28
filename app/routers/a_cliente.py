from typing import List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_cliente import (
    a_actualizar_cliente,
    a_crear_cliente,
    a_eliminar_cliente,
    a_listar_clientes,
    a_obtener_cliente,
)
from app.controllers.a_pedido import a_pedidos_por_cliente
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_cliente import A_ClienteCreate, A_ClienteResponse, A_ClienteUpdate
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_pedido import A_PedidoResponse

a_router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Clientes"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "CAJERO"]))],
)


@a_router.get("", response_model=List[A_ClienteResponse], summary="Listar clientes")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_clientes(a_db=a_db)


@a_router.get(
    "/{id}/pedidos",
    response_model=List[A_PedidoResponse],
    summary="Historial de pedidos de un cliente",
    responses={404: {"description": "Cliente no encontrado"}},
)
def a_pedidos(id: int, a_db: Database = Depends(a_get_db)):
    return a_pedidos_por_cliente(a_db=a_db, a_id_cliente=id)


@a_router.get(
    "/{id}",
    response_model=A_ClienteResponse,
    summary="Obtener cliente por ID",
    responses={404: {"description": "Cliente no encontrado"}},
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_cliente(a_db=a_db, a_id_cliente=id)


@a_router.post(
    "",
    response_model=A_ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cliente",
    responses={409: {"description": "Documento duplicado"}},
)
def a_crear(a_datos: A_ClienteCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_cliente(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_ClienteResponse,
    summary="Actualizar cliente",
    responses={404: {"description": "Cliente no encontrado"}, 409: {"description": "Documento duplicado"}},
)
def a_actualizar(id: int, a_datos: A_ClienteUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_cliente(a_db=a_db, a_id_cliente=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar cliente",
    description="RN04: si tiene pedidos se cambia a INACTIVO (borrado lógico).",
    responses={404: {"description": "Cliente no encontrado"}},
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_cliente(a_db=a_db, a_id_cliente=id)
