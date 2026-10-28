from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_pedido import (
    a_actualizar_pedido,
    a_cambiar_estado_pedido,
    a_crear_pedido,
    a_eliminar_pedido,
    a_listar_pedidos,
    a_obtener_pedido,
    a_pedidos_por_estado,
)
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_pedido import (
    A_EstadoPedido,
    A_PedidoCreate,
    A_PedidoEstadoUpdate,
    A_PedidoResponse,
    A_PedidoUpdate,
)

# CRUD: ADMIN y CAJERO. Consulta por estado y cambio de estado: también COCINERO.
a_router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])
a_admin_cajero = [Depends(a_requerir_roles(["ADMIN", "CAJERO"]))]
a_con_cocinero = [Depends(a_requerir_roles(["ADMIN", "CAJERO", "COCINERO"]))]


@a_router.get("", response_model=List[A_PedidoResponse], summary="Listar pedidos", dependencies=a_admin_cajero)
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_pedidos(a_db=a_db)


@a_router.get(
    "/estado/{estado}",
    response_model=List[A_PedidoResponse],
    summary="Pedidos por estado",
    description="Estados: PENDIENTE, EN_PREPARACION, ENTREGADO, ANULADO.",
    dependencies=a_con_cocinero,
)
def a_por_estado(estado: A_EstadoPedido, a_db: Database = Depends(a_get_db)):
    return a_pedidos_por_estado(a_db=a_db, a_estado=estado)


@a_router.patch(
    "/{id}/estado",
    response_model=A_PedidoResponse,
    summary="Cambiar estado del pedido",
    description=(
        "Flujo: PENDIENTE → EN_PREPARACION → ENTREGADO (o ANULADO desde los dos primeros). "
        "RN03: al pasar a ENTREGADO descuenta los insumos según la receta (409 si no alcanzan). "
        "RN05: un pedido ENTREGADO o ANULADO no se puede modificar (409)."
    ),
    responses={404: {"description": "Pedido no encontrado"}, 409: {"description": "Stock insuficiente o transición no permitida"}},
    dependencies=a_con_cocinero,
)
def a_cambiar_estado(id: int, a_datos: A_PedidoEstadoUpdate, a_db: Database = Depends(a_get_db)):
    return a_cambiar_estado_pedido(a_db=a_db, a_id_pedido=id, a_nuevo_estado=a_datos.estado)


@a_router.get(
    "/{id}",
    response_model=A_PedidoResponse,
    summary="Obtener pedido por ID",
    responses={404: {"description": "Pedido no encontrado"}},
    dependencies=a_admin_cajero,
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_pedido(a_db=a_db, a_id_pedido=id)


@a_router.post(
    "",
    response_model=A_PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pedido con su detalle",
    description="RN01: la API toma el precio de cada producto y calcula subtotales y total.",
    responses={404: {"description": "Cliente o producto no existe"}, 409: {"description": "Producto no disponible o cliente inactivo"}},
)
def a_crear(
    a_datos: A_PedidoCreate,
    a_db: Database = Depends(a_get_db),
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "CAJERO"])),
):
    return a_crear_pedido(a_db=a_db, a_datos=a_datos, a_id_usuario=a_usuario["id_usuario"])


@a_router.put(
    "/{id}",
    response_model=A_PedidoResponse,
    summary="Actualizar datos del pedido",
    description="Permite cambiar tipo_pedido y observaciones (RN05: no si está ENTREGADO o ANULADO).",
    responses={404: {"description": "Pedido no encontrado"}, 409: {"description": "Pedido no modificable (RN05)"}},
    dependencies=a_admin_cajero,
)
def a_actualizar(id: int, a_datos: A_PedidoUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_pedido(a_db=a_db, a_id_pedido=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar pedido",
    description="Solo pedidos PENDIENTE o ANULADO.",
    responses={404: {"description": "Pedido no encontrado"}, 409: {"description": "Pedido en preparación o entregado"}},
    dependencies=a_admin_cajero,
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_pedido(a_db=a_db, a_id_pedido=id)
