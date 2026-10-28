from typing import List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_compra import a_compras_por_proveedor
from app.controllers.a_proveedor import (
    a_actualizar_proveedor,
    a_crear_proveedor,
    a_eliminar_proveedor,
    a_listar_proveedores,
    a_obtener_proveedor,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_compra import A_CompraResponse
from app.schemas.a_proveedor import A_ProveedorCreate, A_ProveedorResponse, A_ProveedorUpdate

a_router = APIRouter(
    prefix="/api/v1/proveedores",
    tags=["Proveedores"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_router.get("", response_model=List[A_ProveedorResponse], summary="Listar proveedores")
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_proveedores(a_db=a_db)


@a_router.get(
    "/{id}/compras",
    response_model=List[A_CompraResponse],
    summary="Historial de compras a un proveedor",
    responses={404: {"description": "Proveedor no encontrado"}},
)
def a_compras(id: int, a_db: Database = Depends(a_get_db)):
    return a_compras_por_proveedor(a_db=a_db, a_id_proveedor=id)


@a_router.get(
    "/{id}",
    response_model=A_ProveedorResponse,
    summary="Obtener proveedor por ID",
    responses={404: {"description": "Proveedor no encontrado"}},
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_proveedor(a_db=a_db, a_id_proveedor=id)


@a_router.post(
    "",
    response_model=A_ProveedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proveedor",
    responses={409: {"description": "NIT duplicado"}},
)
def a_crear(a_datos: A_ProveedorCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_proveedor(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_ProveedorResponse,
    summary="Actualizar proveedor",
    responses={404: {"description": "Proveedor no encontrado"}, 409: {"description": "NIT duplicado"}},
)
def a_actualizar(id: int, a_datos: A_ProveedorUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_proveedor(a_db=a_db, a_id_proveedor=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar proveedor",
    description="RN04: si tiene compras se cambia a INACTIVO (borrado lógico).",
    responses={404: {"description": "Proveedor no encontrado"}},
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_proveedor(a_db=a_db, a_id_proveedor=id)
