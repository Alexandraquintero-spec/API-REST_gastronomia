from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_insumo import A_Insumo
from app.models.a_producto import A_Producto
from app.models.a_receta import A_Receta
from app.schemas.a_receta import A_RecetaCreate, A_RecetaUpdate


def a_completar_receta(a_db: Database, a_receta: Dict[str, Any]) -> Dict[str, Any]:
    """Agrega a la receta los datos del insumo (nombre, unidad y costo)."""
    a_insumo = A_Insumo.a_tabla(a_db).find_one({"id_insumo": a_receta["id_insumo"]}) or {}
    a_resultado = a_limpiar_documento(a_receta)
    a_resultado["nombre_insumo"] = a_insumo.get("nombre", "")
    a_resultado["unidad_medida"] = a_insumo.get("unidad_medida", "")
    a_resultado["costo_unitario"] = float(a_insumo.get("costo_unitario", 0.0))
    return a_resultado


def a_validar_producto_insumo(a_db: Database, a_id_producto: int = None, a_id_insumo: int = None) -> None:
    if a_id_producto is not None and not A_Producto.a_tabla(a_db).find_one({"id_producto": a_id_producto}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if a_id_insumo is not None and not A_Insumo.a_tabla(a_db).find_one({"id_insumo": a_id_insumo}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")


def a_listar_recetas(a_db: Database) -> List[Dict[str, Any]]:
    return [a_completar_receta(a_db, a_r) for a_r in A_Receta.a_tabla(a_db).find()]


def a_obtener_receta(a_db: Database, a_id_receta: int) -> Dict[str, Any]:
    a_receta = A_Receta.a_tabla(a_db).find_one({"id_receta": a_id_receta})
    if not a_receta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    return a_completar_receta(a_db, a_receta)


def a_receta_por_producto(a_db: Database, a_id_producto: int) -> List[Dict[str, Any]]:
    a_validar_producto_insumo(a_db, a_id_producto=a_id_producto)
    return [a_completar_receta(a_db, a_r) for a_r in A_Receta.a_tabla(a_db).find({"id_producto": a_id_producto})]


def a_crear_receta(a_db: Database, a_datos: A_RecetaCreate) -> Dict[str, Any]:
    a_validar_producto_insumo(a_db, a_datos.id_producto, a_datos.id_insumo)
    a_col = A_Receta.a_tabla(a_db)
    if a_col.find_one({"id_producto": a_datos.id_producto, "id_insumo": a_datos.id_insumo}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ese insumo ya está en la receta del producto; actualice la cantidad con PUT",
        )
    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_receta"] = a_obtener_siguiente_id(a_db, A_Receta.a_coleccion)
    a_col.insert_one(a_nuevo_doc)
    return a_completar_receta(a_db, a_nuevo_doc)


def a_actualizar_receta(a_db: Database, a_id_receta: int, a_datos: A_RecetaUpdate) -> Dict[str, Any]:
    a_obtener_receta(a_db, a_id_receta)
    a_cambios = a_datos.model_dump(exclude_none=True)
    a_validar_producto_insumo(a_db, a_cambios.get("id_producto"), a_cambios.get("id_insumo"))
    if a_cambios:
        A_Receta.a_tabla(a_db).update_one({"id_receta": a_id_receta}, {"$set": a_cambios})
    return a_obtener_receta(a_db, a_id_receta)


def a_eliminar_receta(a_db: Database, a_id_receta: int) -> Dict[str, str]:
    a_obtener_receta(a_db, a_id_receta)
    A_Receta.a_tabla(a_db).delete_one({"id_receta": a_id_receta})
    return {"mensaje": f"Ítem de receta con ID {a_id_receta} eliminado exitosamente", "tipo_borrado": "FISICO"}
