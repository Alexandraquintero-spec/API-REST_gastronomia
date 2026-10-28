from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_compra import A_Compra
from app.models.a_proveedor import A_Proveedor
from app.schemas.a_proveedor import A_ProveedorCreate, A_ProveedorUpdate


def a_listar_proveedores(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_p) for a_p in A_Proveedor.a_tabla(a_db).find()]


def a_obtener_proveedor(a_db: Database, a_id_proveedor: int) -> Dict[str, Any]:
    a_proveedor = A_Proveedor.a_tabla(a_db).find_one({"id_proveedor": a_id_proveedor})
    if not a_proveedor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
    return a_limpiar_documento(a_proveedor)


def a_crear_proveedor(a_db: Database, a_datos: A_ProveedorCreate) -> Dict[str, Any]:
    a_col = A_Proveedor.a_tabla(a_db)
    if a_col.find_one({"nit": a_datos.nit}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El NIT de proveedor ya existe")
    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_proveedor"] = a_obtener_siguiente_id(a_db, A_Proveedor.a_coleccion)
    a_col.insert_one(a_nuevo_doc)
    return a_limpiar_documento(a_nuevo_doc)


def a_actualizar_proveedor(a_db: Database, a_id_proveedor: int, a_datos: A_ProveedorUpdate) -> Dict[str, Any]:
    a_col = A_Proveedor.a_tabla(a_db)
    a_proveedor = a_obtener_proveedor(a_db, a_id_proveedor)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if "nit" in a_cambios and a_cambios["nit"] != a_proveedor["nit"]:
        if a_col.find_one({"nit": a_cambios["nit"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El NIT de proveedor ya existe")
    if a_cambios:
        a_col.update_one({"id_proveedor": a_id_proveedor}, {"$set": a_cambios})
    return a_obtener_proveedor(a_db, a_id_proveedor)


def a_eliminar_proveedor(a_db: Database, a_id_proveedor: int) -> Dict[str, str]:
    """RN04: borrado lógico si tiene compras; físico si no."""
    a_col = A_Proveedor.a_tabla(a_db)
    a_obtener_proveedor(a_db, a_id_proveedor)
    if A_Compra.a_tabla(a_db).find_one({"id_proveedor": a_id_proveedor}):
        a_col.update_one({"id_proveedor": a_id_proveedor}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Proveedor con ID {a_id_proveedor} tiene compras registradas. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    a_col.delete_one({"id_proveedor": a_id_proveedor})
    return {"mensaje": f"Proveedor con ID {a_id_proveedor} eliminado físicamente", "tipo_borrado": "FISICO"}
