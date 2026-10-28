from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.controllers.a_categoria import a_obtener_categoria
from app.controllers.a_receta import a_receta_por_producto
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_categoria import A_Categoria
from app.models.a_pedido import A_Pedido
from app.models.a_producto import A_Producto
from app.models.a_receta import A_Receta
from app.schemas.a_producto import A_ProductoCreate, A_ProductoUpdate


def a_listar_productos(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_p) for a_p in A_Producto.a_tabla(a_db).find()]


def a_obtener_producto(a_db: Database, a_id_producto: int) -> Dict[str, Any]:
    a_producto = A_Producto.a_tabla(a_db).find_one({"id_producto": a_id_producto})
    if not a_producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return a_limpiar_documento(a_producto)


def a_productos_por_categoria(a_db: Database, a_id_categoria: int) -> List[Dict[str, Any]]:
    a_obtener_categoria(a_db, a_id_categoria)
    return [a_limpiar_documento(a_p) for a_p in A_Producto.a_tabla(a_db).find({"id_categoria": a_id_categoria})]


def a_validar_categoria(a_db: Database, a_id_categoria: int) -> None:
    if not A_Categoria.a_tabla(a_db).find_one({"id_categoria": a_id_categoria}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La categoría especificada no existe")


def a_crear_producto(a_db: Database, a_datos: A_ProductoCreate) -> Dict[str, Any]:
    a_col = A_Producto.a_tabla(a_db)
    if a_col.find_one({"codigo": a_datos.codigo}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de producto ya existe")
    a_validar_categoria(a_db, a_datos.id_categoria)

    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_producto"] = a_obtener_siguiente_id(a_db, A_Producto.a_coleccion)
    a_col.insert_one(a_nuevo_doc)
    return a_limpiar_documento(a_nuevo_doc)


def a_actualizar_producto(a_db: Database, a_id_producto: int, a_datos: A_ProductoUpdate) -> Dict[str, Any]:
    a_col = A_Producto.a_tabla(a_db)
    a_producto = a_obtener_producto(a_db, a_id_producto)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if "codigo" in a_cambios and a_cambios["codigo"] != a_producto["codigo"]:
        if a_col.find_one({"codigo": a_cambios["codigo"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de producto ya existe")
    if "id_categoria" in a_cambios:
        a_validar_categoria(a_db, a_cambios["id_categoria"])
    if a_cambios:
        a_col.update_one({"id_producto": a_id_producto}, {"$set": a_cambios})
    return a_obtener_producto(a_db, a_id_producto)


def a_eliminar_producto(a_db: Database, a_id_producto: int) -> Dict[str, str]:
    """RN04: borrado lógico (INACTIVO) si tiene recetas o pedidos; físico si no."""
    a_col = A_Producto.a_tabla(a_db)
    a_obtener_producto(a_db, a_id_producto)

    a_tiene_receta = A_Receta.a_tabla(a_db).find_one({"id_producto": a_id_producto}) is not None
    a_tiene_pedidos = A_Pedido.a_tabla(a_db).find_one({"detalles.id_producto": a_id_producto}) is not None
    if a_tiene_receta or a_tiene_pedidos:
        a_col.update_one({"id_producto": a_id_producto}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Producto con ID {a_id_producto} tiene movimientos asociados. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    a_col.delete_one({"id_producto": a_id_producto})
    return {"mensaje": f"Producto con ID {a_id_producto} eliminado físicamente", "tipo_borrado": "FISICO"}


def a_calcular_costo_produccion(a_db: Database, a_id_producto: int) -> Dict[str, Any]:
    """RF06: costo = Σ (cantidad × costo_unitario) y margen frente al precio de venta."""
    a_producto = a_obtener_producto(a_db, a_id_producto)
    a_receta = a_receta_por_producto(a_db, a_id_producto)

    a_costo_total = sum(float(a_r["cantidad"]) * a_r["costo_unitario"] for a_r in a_receta)
    a_precio_venta = float(a_producto["precio_venta"])
    a_margen = a_precio_venta - a_costo_total
    a_porcentaje = (a_margen / a_precio_venta * 100.0) if a_precio_venta > 0 else 0.0

    return {
        "id_producto": a_producto["id_producto"],
        "codigo": a_producto["codigo"],
        "nombre": a_producto["nombre"],
        "precio_venta": a_precio_venta,
        "costo_produccion": round(a_costo_total, 2),
        "margen_ganancia": round(a_margen, 2),
        "porcentaje_margen": round(a_porcentaje, 2),
        "receta": a_receta,
    }
