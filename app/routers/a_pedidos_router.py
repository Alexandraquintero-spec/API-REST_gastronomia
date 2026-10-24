from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_PedidoCreate,
    A_PedidoEstadoUpdate,
    A_PedidoResponse,
)
from app.controllers import a_controllers

a_pedidos_router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@a_pedidos_router.get(
    "",
    response_model=List[A_PedidoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar pedidos",
    description="Retorna el listado de pedidos registrados (ADMIN, CAJERO).",
    responses={
        200: {"description": "Lista de pedidos"},
    },
)
def a_listar_pedidos(
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO"])),
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_listar_pedidos(a_db)


@a_pedidos_router.get(
    "/estado/{estado}",
    response_model=List[A_PedidoResponse],
    status_code=status.HTTP_200_OK,
    summary="Filtrar pedidos por estado",
    description="Retorna pedidos filtrados por estado: PENDIENTE, EN_PREPARACION, ENTREGADO o ANULADO (ADMIN, CAJERO, COCINERO).",
    responses={
        200: {"description": "Pedidos en el estado consultado"},
        400: {"description": "Estado inválido"},
    },
)
def a_pedidos_por_estado(
    estado: str,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO", "COCINERO"])),
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_pedidos_por_estado(a_db, estado)


@a_pedidos_router.patch(
    "/{id}/estado",
    response_model=A_PedidoResponse,
    status_code=status.HTTP_200_OK,
    summary="Cambiar estado del pedido",
    description=(
        "Actualiza el estado del pedido (PENDIENTE → EN_PREPARACION → ENTREGADO / ANULADO). "
        "Aplica RN03 (descuento de insumos o 409 si falta stock al pasar a ENTREGADO) "
        "y RN05 (impide modificar si ya está ENTREGADO o ANULADO). Permitido para ADMIN y COCINERO."
    ),
    responses={
        200: {"description": "Estado actualizado exitosamente"},
        404: {"description": "Pedido no encontrado"},
        409: {"description": "Conflicto por stock insuficiente (RN03) o estado no modificable (RN05)"},
    },
)
def a_cambiar_estado_pedido(
    id: int,
    a_datos: A_PedidoEstadoUpdate,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "COCINERO"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_cambiar_estado_pedido(a_db, id, a_datos.estado)


@a_pedidos_router.get(
    "/{id}",
    response_model=A_PedidoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener pedido por ID",
    description="Retorna la información completa de un pedido con sus detalles calculados (ADMIN, CAJERO).",
    responses={
        200: {"description": "Pedido encontrado"},
        404: {"description": "Pedido no encontrado"},
    },
)
def a_obtener_pedido(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_obtener_pedido(a_db, id)


@a_pedidos_router.post(
    "",
    response_model=A_PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pedido con detalle",
    description=(
        "Registra un nuevo pedido. Aplica la RN01: subtotal = cantidad * precio_unitario y total = suma de subtotales, "
        "calculados por la API tomando el precio actual del producto (se ignora cualquier valor enviado por el cliente). (ADMIN, CAJERO)."
    ),
    responses={
        201: {"description": "Pedido creado exitosamente con totales calculados"},
        404: {"description": "Cliente o producto no encontrado"},
        409: {"description": "Producto no disponible"},
    },
)
def a_crear_pedido(
    a_datos: A_PedidoCreate,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    a_id_usuario = a_usuario.get("id_usuario", 1)
    return a_controllers.a_crear_pedido(a_db, a_datos, a_id_usuario)


@a_pedidos_router.put(
    "/{id}",
    response_model=A_PedidoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar pedido",
    description="Actualiza campos de cabecera de un pedido antes de ser entregado o anulado (RN05) (ADMIN, CAJERO).",
    responses={
        200: {"description": "Pedido actualizado"},
        404: {"description": "Pedido no encontrado"},
        409: {"description": "No modificable por estado ENTREGADO o ANULADO (RN05)"},
    },
)
def a_actualizar_pedido(
    id: int,
    a_datos: Dict[str, Any],
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_actualizar_pedido(a_db, id, a_datos)


@a_pedidos_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar pedido",
    description="Elimina un pedido del sistema si se encuentra en estado inicial PENDIENTE o ANULADO (ADMIN, CAJERO).",
    responses={
        200: {"description": "Pedido eliminado"},
        404: {"description": "Pedido no encontrado"},
        409: {"description": "No se puede eliminar un pedido en preparación o entregado"},
    },
)
def a_eliminar_pedido(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_controllers.a_eliminar_pedido(a_db, id)
