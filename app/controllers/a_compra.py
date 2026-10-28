from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.controllers.a_proveedor import a_obtener_proveedor
from app.core.a_config import a_fecha_actual
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_compra import A_Compra
from app.models.a_insumo import A_Insumo
from app.schemas.a_compra import A_CompraCreate, A_CompraUpdate


def a_listar_compras(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_c) for a_c in A_Compra.a_tabla(a_db).find().sort("fecha_compra", -1)]


def a_obtener_compra(a_db: Database, a_id_compra: int) -> Dict[str, Any]:
    a_compra = A_Compra.a_tabla(a_db).find_one({"id_compra": a_id_compra})
    if not a_compra:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada")
    return a_limpiar_documento(a_compra)


def a_compras_por_proveedor(a_db: Database, a_id_proveedor: int) -> List[Dict[str, Any]]:
    a_obtener_proveedor(a_db, a_id_proveedor)
    a_compras = A_Compra.a_tabla(a_db).find({"id_proveedor": a_id_proveedor}).sort("fecha_compra", -1)
    return [a_limpiar_documento(a_c) for a_c in a_compras]


def a_crear_compra(a_db: Database, a_datos: A_CompraCreate, a_id_usuario: int) -> Dict[str, Any]:
    """RN02: suma la cantidad al stock_actual y actualiza el costo_unitario de cada insumo."""
    a_obtener_proveedor(a_db, a_datos.id_proveedor)
    a_col_insumos = A_Insumo.a_tabla(a_db)

    # 1. Validar todos los insumos antes de modificar el inventario
    a_insumos = {}
    for a_item in a_datos.detalles:
        a_insumo = a_col_insumos.find_one({"id_insumo": a_item.id_insumo})
        if not a_insumo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Insumo con ID {a_item.id_insumo} no existe")
        a_insumos[a_item.id_insumo] = a_insumo

    # 2. Calcular detalle y total
    a_detalles = []
    a_total = 0.0
    for a_numero, a_item in enumerate(a_datos.detalles, start=1):
        a_subtotal = round(a_item.cantidad * a_item.costo_unitario, 2)
        a_total += a_subtotal
        a_detalles.append(
            {
                "id_detalle_compra": a_numero,
                "id_insumo": a_item.id_insumo,
                "nombre_insumo": a_insumos[a_item.id_insumo]["nombre"],
                "cantidad": a_item.cantidad,
                "costo_unitario": a_item.costo_unitario,
                "subtotal": a_subtotal,
            }
        )

    # 3. RN02: actualizar existencias (redondeadas a 3 decimales) y costo unitario
    for a_item in a_datos.detalles:
        a_col_insumos.update_one(
            {"id_insumo": a_item.id_insumo},
            [
                {
                    "$set": {
                        "stock_actual": {"$round": [{"$add": ["$stock_actual", a_item.cantidad]}, 3]},
                        "costo_unitario": a_item.costo_unitario,
                    }
                }
            ],
        )

    a_nueva_compra = {
        "id_compra": a_obtener_siguiente_id(a_db, A_Compra.a_coleccion),
        "numero_factura": a_datos.numero_factura,
        "fecha_compra": a_fecha_actual(),
        "id_proveedor": a_datos.id_proveedor,
        "id_usuario": a_id_usuario,
        "total": round(a_total, 2),
        "detalles": a_detalles,
    }
    A_Compra.a_tabla(a_db).insert_one(a_nueva_compra)
    return a_limpiar_documento(a_nueva_compra)


def a_actualizar_compra(a_db: Database, a_id_compra: int, a_datos: A_CompraUpdate) -> Dict[str, Any]:
    a_obtener_compra(a_db, a_id_compra)
    A_Compra.a_tabla(a_db).update_one({"id_compra": a_id_compra}, {"$set": {"numero_factura": a_datos.numero_factura}})
    return a_obtener_compra(a_db, a_id_compra)


def a_eliminar_compra(a_db: Database, a_id_compra: int) -> Dict[str, str]:
    """Anula la compra y revierte las existencias que sumó (RN02 inverso)."""
    a_compra = a_obtener_compra(a_db, a_id_compra)
    a_col_insumos = A_Insumo.a_tabla(a_db)

    for a_det in a_compra.get("detalles", []):
        a_insumo = a_col_insumos.find_one({"id_insumo": a_det["id_insumo"]})
        if a_insumo and float(a_insumo.get("stock_actual", 0)) < float(a_det["cantidad"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede eliminar: el insumo '{a_insumo['nombre']}' ya se consumió y quedaría en negativo",
            )
    for a_det in a_compra.get("detalles", []):
        a_col_insumos.update_one(
            {"id_insumo": a_det["id_insumo"]},
            [{"$set": {"stock_actual": {"$round": [{"$subtract": ["$stock_actual", float(a_det["cantidad"])]}, 3]}}}],
        )

    A_Compra.a_tabla(a_db).delete_one({"id_compra": a_id_compra})
    return {"mensaje": f"Compra con ID {a_id_compra} eliminada y existencias revertidas", "tipo_borrado": "FISICO"}
