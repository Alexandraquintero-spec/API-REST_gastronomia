from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_cliente import A_Cliente
from app.models.a_pedido import A_Pedido
from app.schemas.a_cliente import A_ClienteCreate, A_ClienteUpdate


def a_listar_clientes(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_c) for a_c in A_Cliente.a_tabla(a_db).find()]


def a_obtener_cliente(a_db: Database, a_id_cliente: int) -> Dict[str, Any]:
    a_cliente = A_Cliente.a_tabla(a_db).find_one({"id_cliente": a_id_cliente})
    if not a_cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return a_limpiar_documento(a_cliente)


def a_crear_cliente(a_db: Database, a_datos: A_ClienteCreate) -> Dict[str, Any]:
    a_col = A_Cliente.a_tabla(a_db)
    if a_col.find_one({"identificacion": a_datos.identificacion}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento de identidad ya existe")
    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_cliente"] = a_obtener_siguiente_id(a_db, A_Cliente.a_coleccion)
    a_col.insert_one(a_nuevo_doc)
    return a_limpiar_documento(a_nuevo_doc)


def a_actualizar_cliente(a_db: Database, a_id_cliente: int, a_datos: A_ClienteUpdate) -> Dict[str, Any]:
    a_col = A_Cliente.a_tabla(a_db)
    a_cliente = a_obtener_cliente(a_db, a_id_cliente)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if "identificacion" in a_cambios and a_cambios["identificacion"] != a_cliente["identificacion"]:
        if a_col.find_one({"identificacion": a_cambios["identificacion"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento de identidad ya existe")
    if a_cambios:
        a_col.update_one({"id_cliente": a_id_cliente}, {"$set": a_cambios})
    return a_obtener_cliente(a_db, a_id_cliente)


def a_eliminar_cliente(a_db: Database, a_id_cliente: int) -> Dict[str, str]:
    """RN04: borrado lógico si tiene pedidos; físico si no."""
    a_col = A_Cliente.a_tabla(a_db)
    a_obtener_cliente(a_db, a_id_cliente)
    if A_Pedido.a_tabla(a_db).find_one({"id_cliente": a_id_cliente}):
        a_col.update_one({"id_cliente": a_id_cliente}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Cliente con ID {a_id_cliente} tiene pedidos registrados. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    a_col.delete_one({"id_cliente": a_id_cliente})
    return {"mensaje": f"Cliente con ID {a_id_cliente} eliminado físicamente", "tipo_borrado": "FISICO"}
