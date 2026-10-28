from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.controllers.a_cliente import a_obtener_cliente
from app.core.a_config import a_fecha_actual
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_insumo import A_Insumo
from app.models.a_pedido import A_Pedido
from app.models.a_producto import A_Producto
from app.models.a_receta import A_Receta
from app.schemas.a_pedido import A_PedidoCreate, A_PedidoUpdate

A_ESTADOS_FINALES = ("ENTREGADO", "ANULADO")

# Transiciones de estado permitidas
A_TRANSICIONES = {
    "PENDIENTE": ("EN_PREPARACION", "ANULADO"),
    "EN_PREPARACION": ("ENTREGADO", "ANULADO"),
}


def a_listar_pedidos(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_p) for a_p in A_Pedido.a_tabla(a_db).find().sort("fecha_pedido", -1)]


def a_obtener_pedido(a_db: Database, a_id_pedido: int) -> Dict[str, Any]:
    a_pedido = A_Pedido.a_tabla(a_db).find_one({"id_pedido": a_id_pedido})
    if not a_pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return a_limpiar_documento(a_pedido)


def a_pedidos_por_cliente(a_db: Database, a_id_cliente: int) -> List[Dict[str, Any]]:
    a_obtener_cliente(a_db, a_id_cliente)
    a_pedidos = A_Pedido.a_tabla(a_db).find({"id_cliente": a_id_cliente}).sort("fecha_pedido", -1)
    return [a_limpiar_documento(a_p) for a_p in a_pedidos]


def a_pedidos_por_estado(a_db: Database, a_estado: str) -> List[Dict[str, Any]]:
    a_pedidos = A_Pedido.a_tabla(a_db).find({"estado": a_estado}).sort("fecha_pedido", -1)
    return [a_limpiar_documento(a_p) for a_p in a_pedidos]


def a_validar_modificable(a_pedido: Dict[str, Any]) -> None:
    """RN05: un pedido ENTREGADO o ANULADO no puede modificarse."""
    if a_pedido["estado"] in A_ESTADOS_FINALES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un pedido en estado '{a_pedido['estado']}' no puede modificarse (RN05)",
        )


def a_crear_pedido(a_db: Database, a_datos: A_PedidoCreate, a_id_usuario: int) -> Dict[str, Any]:
    """RN01: subtotal = cantidad × precio_unitario y total = Σ subtotales, calculados por la API."""
    a_cliente = a_obtener_cliente(a_db, a_datos.id_cliente)
    if a_cliente.get("estado") != "ACTIVO":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El cliente se encuentra INACTIVO")

    a_detalles = []
    a_total = 0.0
    for a_numero, a_item in enumerate(a_datos.detalles, start=1):
        a_producto = A_Producto.a_tabla(a_db).find_one({"id_producto": a_item.id_producto})
        if not a_producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto con ID {a_item.id_producto} no encontrado")
        if a_producto.get("estado") != "DISPONIBLE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto '{a_producto['nombre']}' no está disponible (estado: {a_producto.get('estado')})",
            )

        # RN01: el precio se toma del producto, nunca del cliente
        a_precio_unitario = float(a_producto["precio_venta"])
        a_subtotal = round(a_item.cantidad * a_precio_unitario, 2)
        a_total += a_subtotal
        a_detalles.append(
            {
                "id_detalle": a_numero,
                "id_producto": a_item.id_producto,
                "nombre_producto": a_producto["nombre"],
                "cantidad": a_item.cantidad,
                "precio_unitario": a_precio_unitario,
                "subtotal": a_subtotal,
            }
        )

    a_nuevo_pedido = {
        "id_pedido": a_obtener_siguiente_id(a_db, A_Pedido.a_coleccion),
        "fecha_pedido": a_fecha_actual(),
        "id_cliente": a_datos.id_cliente,
        "id_usuario": a_id_usuario,
        "tipo_pedido": a_datos.tipo_pedido,
        "estado": "PENDIENTE",
        "total": round(a_total, 2),
        "observaciones": a_datos.observaciones,
        "detalles": a_detalles,
    }
    A_Pedido.a_tabla(a_db).insert_one(a_nuevo_pedido)
    return a_limpiar_documento(a_nuevo_pedido)


def a_descontar_inventario(a_db: Database, a_pedido: Dict[str, Any]) -> None:
    """RN03: descuenta los insumos según la receta de cada producto; 409 si no alcanza."""
    a_requeridos: Dict[int, float] = {}
    for a_det in a_pedido.get("detalles", []):
        for a_receta in A_Receta.a_tabla(a_db).find({"id_producto": a_det["id_producto"]}):
            a_requeridos[a_receta["id_insumo"]] = (
                a_requeridos.get(a_receta["id_insumo"], 0.0) + float(a_receta["cantidad"]) * a_det["cantidad"]
            )

    a_col_insumos = A_Insumo.a_tabla(a_db)
    # 1. Validar todo antes de descontar (no se deja el inventario a medias)
    for a_id_insumo, a_cantidad in a_requeridos.items():
        a_insumo = a_col_insumos.find_one({"id_insumo": a_id_insumo})
        a_existencias = float(a_insumo.get("stock_actual", 0.0)) if a_insumo else 0.0
        if a_existencias < a_cantidad:
            a_nombre = a_insumo["nombre"] if a_insumo else f"ID {a_id_insumo}"
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock insuficiente para '{a_nombre}'. Existencias: {a_existencias}, requerido: {round(a_cantidad, 3)} (RN03)",
            )
    # 2. Descontar (redondeado a 3 decimales para no acumular error de punto flotante)
    for a_id_insumo, a_cantidad in a_requeridos.items():
        a_col_insumos.update_one(
            {"id_insumo": a_id_insumo},
            [{"$set": {"stock_actual": {"$round": [{"$subtract": ["$stock_actual", a_cantidad]}, 3]}}}],
        )


def a_cambiar_estado_pedido(a_db: Database, a_id_pedido: int, a_nuevo_estado: str) -> Dict[str, Any]:
    """Cambia el estado aplicando RN05 (estados finales) y RN03 (descuento de inventario)."""
    a_pedido = a_obtener_pedido(a_db, a_id_pedido)
    a_validar_modificable(a_pedido)

    a_permitidos = A_TRANSICIONES[a_pedido["estado"]]
    if a_nuevo_estado not in a_permitidos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transición no permitida: de {a_pedido['estado']} solo se puede pasar a {' o '.join(a_permitidos)}",
        )

    if a_nuevo_estado == "ENTREGADO":
        a_descontar_inventario(a_db, a_pedido)

    A_Pedido.a_tabla(a_db).update_one({"id_pedido": a_id_pedido}, {"$set": {"estado": a_nuevo_estado}})
    return a_obtener_pedido(a_db, a_id_pedido)


def a_actualizar_pedido(a_db: Database, a_id_pedido: int, a_datos: A_PedidoUpdate) -> Dict[str, Any]:
    a_pedido = a_obtener_pedido(a_db, a_id_pedido)
    a_validar_modificable(a_pedido)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if a_cambios:
        A_Pedido.a_tabla(a_db).update_one({"id_pedido": a_id_pedido}, {"$set": a_cambios})
    return a_obtener_pedido(a_db, a_id_pedido)


def a_eliminar_pedido(a_db: Database, a_id_pedido: int) -> Dict[str, str]:
    """Solo se eliminan pedidos PENDIENTE o ANULADO (nunca afectaron el inventario)."""
    a_pedido = a_obtener_pedido(a_db, a_id_pedido)
    if a_pedido["estado"] in ("EN_PREPARACION", "ENTREGADO"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar un pedido en estado {a_pedido['estado']}; use PATCH /estado para anularlo",
        )
    A_Pedido.a_tabla(a_db).delete_one({"id_pedido": a_id_pedido})
    return {"mensaje": f"Pedido con ID {a_id_pedido} eliminado exitosamente", "tipo_borrado": "FISICO"}
