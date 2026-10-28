from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_categoria import A_Categoria
from app.models.a_producto import A_Producto
from app.schemas.a_categoria import A_CategoriaCreate, A_CategoriaUpdate


def a_listar_categorias(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_c) for a_c in A_Categoria.a_tabla(a_db).find()]


def a_obtener_categoria(a_db: Database, a_id_categoria: int) -> Dict[str, Any]:
    a_categoria = A_Categoria.a_tabla(a_db).find_one({"id_categoria": a_id_categoria})
    if not a_categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return a_limpiar_documento(a_categoria)


def a_crear_categoria(a_db: Database, a_datos: A_CategoriaCreate) -> Dict[str, Any]:
    a_col = A_Categoria.a_tabla(a_db)
    if a_col.find_one({"nombre": a_datos.nombre}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría con ese nombre")
    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_categoria"] = a_obtener_siguiente_id(a_db, A_Categoria.a_coleccion)
    a_col.insert_one(a_nuevo_doc)
    return a_limpiar_documento(a_nuevo_doc)


def a_actualizar_categoria(a_db: Database, a_id_categoria: int, a_datos: A_CategoriaUpdate) -> Dict[str, Any]:
    a_col = A_Categoria.a_tabla(a_db)
    a_categoria = a_obtener_categoria(a_db, a_id_categoria)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if "nombre" in a_cambios and a_cambios["nombre"] != a_categoria["nombre"]:
        if a_col.find_one({"nombre": a_cambios["nombre"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría con ese nombre")
    if a_cambios:
        a_col.update_one({"id_categoria": a_id_categoria}, {"$set": a_cambios})
    return a_obtener_categoria(a_db, a_id_categoria)


def a_eliminar_categoria(a_db: Database, a_id_categoria: int) -> Dict[str, str]:
    """Si la categoría tiene productos se inactiva (borrado lógico); si no, se elimina."""
    a_col = A_Categoria.a_tabla(a_db)
    a_obtener_categoria(a_db, a_id_categoria)
    if A_Producto.a_tabla(a_db).find_one({"id_categoria": a_id_categoria}):
        a_col.update_one({"id_categoria": a_id_categoria}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"La categoría con ID {a_id_categoria} tiene productos asociados. Se cambió a estado INACTIVO",
            "tipo_borrado": "LOGICO",
        }
    a_col.delete_one({"id_categoria": a_id_categoria})
    return {"mensaje": f"Categoría con ID {a_id_categoria} eliminada exitosamente", "tipo_borrado": "FISICO"}
