from datetime import date, timedelta
from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_compra import A_Compra
from app.models.a_insumo import A_Insumo
from app.models.a_receta import A_Receta
from app.schemas.a_insumo import A_InsumoCreate, A_InsumoUpdate


def a_listar_insumos(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_i) for a_i in A_Insumo.a_tabla(a_db).find()]


def a_obtener_insumo(a_db: Database, a_id_insumo: int) -> Dict[str, Any]:
    a_insumo = A_Insumo.a_tabla(a_db).find_one({"id_insumo": a_id_insumo})
    if not a_insumo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
    return a_limpiar_documento(a_insumo)


def a_insumos_stock_bajo(a_db: Database) -> List[Dict[str, Any]]:
    """RF07: insumos con stock_actual <= stock_minimo ($expr compara dos campos del documento)."""
    a_filtro = {"$expr": {"$lte": ["$stock_actual", "$stock_minimo"]}}
    return [a_limpiar_documento(a_i) for a_i in A_Insumo.a_tabla(a_db).find(a_filtro)]


def a_insumos_por_vencer(a_db: Database, a_dias: int = 7) -> List[Dict[str, Any]]:
    """RF07: insumos que vencen entre hoy y los próximos N días."""
    a_hoy = date.today()
    a_filtro = {"fecha_vencimiento": {"$gte": a_hoy.isoformat(), "$lte": (a_hoy + timedelta(days=a_dias)).isoformat()}}
    return [a_limpiar_documento(a_i) for a_i in A_Insumo.a_tabla(a_db).find(a_filtro).sort("fecha_vencimiento", 1)]


def a_crear_insumo(a_db: Database, a_datos: A_InsumoCreate) -> Dict[str, Any]:
    a_col = A_Insumo.a_tabla(a_db)
    if a_col.find_one({"nombre": a_datos.nombre}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un insumo con ese nombre")
    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_insumo"] = a_obtener_siguiente_id(a_db, A_Insumo.a_coleccion)
    a_col.insert_one(a_nuevo_doc)
    return a_limpiar_documento(a_nuevo_doc)


def a_actualizar_insumo(a_db: Database, a_id_insumo: int, a_datos: A_InsumoUpdate) -> Dict[str, Any]:
    a_col = A_Insumo.a_tabla(a_db)
    a_insumo = a_obtener_insumo(a_db, a_id_insumo)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if "nombre" in a_cambios and a_cambios["nombre"] != a_insumo["nombre"]:
        if a_col.find_one({"nombre": a_cambios["nombre"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un insumo con ese nombre")
    if a_cambios:
        a_col.update_one({"id_insumo": a_id_insumo}, {"$set": a_cambios})
    return a_obtener_insumo(a_db, a_id_insumo)


def a_eliminar_insumo(a_db: Database, a_id_insumo: int) -> Dict[str, str]:
    """RN04: borrado lógico si está en recetas o compras; físico si no."""
    a_col = A_Insumo.a_tabla(a_db)
    a_obtener_insumo(a_db, a_id_insumo)

    a_tiene_receta = A_Receta.a_tabla(a_db).find_one({"id_insumo": a_id_insumo}) is not None
    a_tiene_compras = A_Compra.a_tabla(a_db).find_one({"detalles.id_insumo": a_id_insumo}) is not None
    if a_tiene_receta or a_tiene_compras:
        a_col.update_one({"id_insumo": a_id_insumo}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Insumo con ID {a_id_insumo} tiene movimientos en recetas o compras. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    a_col.delete_one({"id_insumo": a_id_insumo})
    return {"mensaje": f"Insumo con ID {a_id_insumo} eliminado físicamente", "tipo_borrado": "FISICO"}
