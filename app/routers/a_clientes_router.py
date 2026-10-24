from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_ClienteCreate,
    A_ClienteResponse,
    A_ClienteUpdate,
    A_PedidoResponse,
)
from app.controllers import a_controllers

a_clientes_router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "CAJERO"]))],
)


@a_clientes_router.get(
    "",
    response_model=List[A_ClienteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar clientes",
    description="Retorna el listado de clientes registrados (aprendices, instructores, funcionarios, externos).",
    responses={
        200: {"description": "Lista de clientes"},
    },
)
def a_listar_clientes(
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_listar_clientes(a_db)


@a_clientes_router.get(
    "/{id}/pedidos",
    response_model=List[A_PedidoResponse],
    status_code=status.HTTP_200_OK,
    summary="Historial de pedidos de un cliente",
    description="Retorna la lista de pedidos realizados por un cliente específico (RF09).",
    responses={
        200: {"description": "Pedidos del cliente"},
        404: {"description": "Cliente no encontrado"},
    },
)
def a_pedidos_de_cliente(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_pedidos_por_cliente(a_db, id)


@a_clientes_router.get(
    "/{id}",
    response_model=A_ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener cliente por ID",
    description="Retorna la información detallada de un cliente.",
    responses={
        200: {"description": "Cliente encontrado"},
        404: {"description": "Cliente no encontrado"},
    },
)
def a_obtener_cliente(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_obtener_cliente(a_db, id)


@a_clientes_router.post(
    "",
    response_model=A_ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cliente",
    description="Registra un nuevo cliente clasificándolo como APRENDIZ, INSTRUCTOR, FUNCIONARIO o EXTERNO.",
    responses={
        201: {"description": "Cliente creado"},
        409: {"description": "Identificación de cliente ya registrada"},
    },
)
def a_crear_cliente(
    a_datos: A_ClienteCreate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_crear_cliente(a_db, a_datos)


@a_clientes_router.put(
    "/{id}",
    response_model=A_ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar cliente",
    description="Actualiza la información de un cliente.",
    responses={
        200: {"description": "Cliente actualizado"},
        404: {"description": "Cliente no encontrado"},
        409: {"description": "Identificación duplicada"},
    },
)
def a_actualizar_cliente(
    id: int,
    a_datos: A_ClienteUpdate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_actualizar_cliente(a_db, id, a_datos)


@a_clientes_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar cliente",
    description="Elimina un cliente. Si tiene pedidos asociados, se aplica borrado lógico a INACTIVO según la RN04.",
    responses={
        200: {"description": "Cliente eliminado o inactivado"},
        404: {"description": "Cliente no encontrado"},
    },
)
def a_eliminar_cliente(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_controllers.a_eliminar_cliente(a_db, id)
