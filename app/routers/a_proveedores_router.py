from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.a_security import a_requerir_roles
from app.database.a_conexion_mysql import a_obtener_db_mysql
from app.schemas.a_schemas import (
    A_CompraResponse,
    A_ProveedorCreate,
    A_ProveedorResponse,
    A_ProveedorUpdate,
)
from app.services.a_services import A_CompraService, A_ProveedorService

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
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_ProveedorResponse]:
    a_servicio = A_ProveedorService(a_db)
    return a_servicio.a_listar_proveedores()


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
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_CompraResponse]:
    a_servicio = A_CompraService(a_db)
    return a_servicio.a_listar_por_proveedor(id)


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
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProveedorResponse:
    a_servicio = A_ProveedorService(a_db)
    return a_servicio.a_obtener_por_id(id)


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
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProveedorResponse:
    a_servicio = A_ProveedorService(a_db)
    return a_servicio.a_crear_proveedor(a_datos)


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
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProveedorResponse:
    a_servicio = A_ProveedorService(a_db)
    return a_servicio.a_actualizar_proveedor(id, a_datos)


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
    a_db: Session = Depends(a_obtener_db_mysql),
) -> Dict[str, str]:
    a_servicio = A_ProveedorService(a_db)
    return a_servicio.a_eliminar_proveedor(id)
