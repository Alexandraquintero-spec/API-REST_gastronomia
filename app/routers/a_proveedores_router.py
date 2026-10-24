from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_CompraResponse,
    A_ProveedorCreate,
    A_ProveedorResponse,
    A_ProveedorUpdate,
)
from app.controllers import a_controllers

a_proveedores_router = APIRouter(
    prefix="/proveedores",
    tags=["Proveedores"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_proveedores_router.get(
    "",
    response_model=List[A_ProveedorResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar proveedores",
    description="Retorna el directorio completo de proveedores de insumos (solo ADMIN).",
    responses={
        200: {"description": "Lista de proveedores"},
    },
)
def a_listar_proveedores(
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_listar_proveedores(a_db)


@a_proveedores_router.get(
    "/{id}/compras",
    response_model=List[A_CompraResponse],
    status_code=status.HTTP_200_OK,
    summary="Historial de compras a un proveedor",
    description="Retorna todas las compras registradas con un proveedor específico.",
    responses={
        200: {"description": "Historial de compras del proveedor"},
        404: {"description": "Proveedor no encontrado"},
    },
)
def a_compras_de_proveedor(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_compras_por_proveedor(a_db, id)


@a_proveedores_router.get(
    "/{id}",
    response_model=A_ProveedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener proveedor por ID",
    description="Retorna los datos de un proveedor específico.",
    responses={
        200: {"description": "Proveedor encontrado"},
        404: {"description": "Proveedor no encontrado"},
    },
)
def a_obtener_proveedor(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_obtener_proveedor(a_db, id)


@a_proveedores_router.post(
    "",
    response_model=A_ProveedorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proveedor",
    description="Registra un nuevo proveedor en el sistema.",
    responses={
        201: {"description": "Proveedor creado"},
        409: {"description": "El NIT ya existe"},
    },
)
def a_crear_proveedor(
    a_datos: A_ProveedorCreate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_crear_proveedor(a_db, a_datos)


@a_proveedores_router.put(
    "/{id}",
    response_model=A_ProveedorResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar proveedor",
    description="Actualiza la información de contacto o estado de un proveedor.",
    responses={
        200: {"description": "Proveedor actualizado"},
        404: {"description": "Proveedor no encontrado"},
        409: {"description": "NIT duplicado"},
    },
)
def a_actualizar_proveedor(
    id: int,
    a_datos: A_ProveedorUpdate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_actualizar_proveedor(a_db, id, a_datos)


@a_proveedores_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar proveedor",
    description="Elimina un proveedor. Si tiene compras registradas, se aplica borrado lógico a INACTIVO según la RN04.",
    responses={
        200: {"description": "Proveedor eliminado o inactivado"},
        404: {"description": "Proveedor no encontrado"},
    },
)
def a_eliminar_proveedor(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_controllers.a_eliminar_proveedor(a_db, id)
