from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_compra import (
    a_actualizar_compra,
    a_crear_compra,
    a_eliminar_compra,
    a_listar_compras,
    a_obtener_compra,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_compra import A_CompraCreate, A_CompraResponse, A_CompraUpdate

a_router = APIRouter(
    prefix="/api/v1/compras",
    tags=["Compras"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_router.get("", response_model=List[A_CompraResponse], summary="Listar compras")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_compras(a_db=a_db)


@a_router.get(
    "/{id}",
    response_model=A_CompraResponse,
    summary="Obtener compra por ID",
    responses={404: {"description": "Compra no encontrada"}},
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_compra(a_db=a_db, a_id_compra=id)


@a_router.post(
    "",
    response_model=A_CompraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar compra de insumos",
    description="RN02: suma la cantidad al stock_actual y actualiza el costo_unitario de cada insumo.",
    responses={404: {"description": "Proveedor o insumo no existe"}},
)
def a_crear(
    a_datos: A_CompraCreate,
    a_db: Database = Depends(a_get_db),
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
):
    return a_crear_compra(a_db=a_db, a_datos=a_datos, a_id_usuario=a_usuario["id_usuario"])


@a_router.put(
    "/{id}",
    response_model=A_CompraResponse,
    summary="Corregir número de factura",
    responses={404: {"description": "Compra no encontrada"}},
)
def a_actualizar(id: int, a_datos: A_CompraUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_compra(a_db=a_db, a_id_compra=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar compra",
    description="Revierte las existencias sumadas por la compra; 409 si ya se consumieron.",
    responses={404: {"description": "Compra no encontrada"}, 409: {"description": "Existencias insuficientes para revertir"}},
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_compra(a_db=a_db, a_id_compra=id)
