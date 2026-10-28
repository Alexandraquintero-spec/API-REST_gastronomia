from typing import Any, Dict, List
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pymongo.database import Database
from app.core.a_config import a_fecha_actual
from app.models.a_calificacion import A_Calificacion
from app.models.a_cliente import A_Cliente
from app.models.a_pedido import A_Pedido
from app.schemas.a_calificacion import A_CalificacionCreate, A_CalificacionUpdate


def a_formatear(a_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte el ObjectId de MongoDB en el campo 'id' (texto)."""
    a_resultado = dict(a_doc)
    a_resultado["id"] = str(a_resultado.pop("_id"))
    return a_resultado


def a_convertir_id(a_id_calificacion: str) -> ObjectId:
    try:
        return ObjectId(a_id_calificacion)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de calificación inválido (debe ser un ObjectId de 24 caracteres hexadecimales)",
        )


def a_listar_calificaciones(a_db: Database) -> List[Dict[str, Any]]:
    return [a_formatear(a_d) for a_d in A_Calificacion.a_tabla(a_db).find().sort("fecha", -1)]


def a_obtener_calificacion(a_db: Database, a_id_calificacion: str) -> Dict[str, Any]:
    a_doc = A_Calificacion.a_tabla(a_db).find_one({"_id": a_convertir_id(a_id_calificacion)})
    if not a_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calificación no encontrada")
    return a_formatear(a_doc)


def a_crear_calificacion(a_db: Database, a_datos: A_CalificacionCreate) -> Dict[str, Any]:
    """RF12: registra la opinión del cliente sobre un pedido y sus productos."""
    a_pedido = A_Pedido.a_tabla(a_db).find_one({"id_pedido": a_datos.id_pedido})
    if not a_pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El pedido calificado no existe")
    if not A_Cliente.a_tabla(a_db).find_one({"id_cliente": a_datos.id_cliente}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente no existe")
    if a_pedido["id_cliente"] != a_datos.id_cliente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El pedido no pertenece a ese cliente")

    a_productos_pedido = {a_d["id_producto"] for a_d in a_pedido.get("detalles", [])}
    a_ajenos = [a_p.id_producto for a_p in a_datos.productos if a_p.id_producto not in a_productos_pedido]
    if a_ajenos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Los productos {a_ajenos} no hacen parte del pedido {a_datos.id_pedido}",
        )

    a_col = A_Calificacion.a_tabla(a_db)
    if a_col.find_one({"id_pedido": a_datos.id_pedido}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este pedido ya fue calificado")

    a_doc = a_datos.model_dump()
    a_doc["fecha"] = a_doc.get("fecha") or a_fecha_actual()
    a_resultado = a_col.insert_one(a_doc)
    return a_obtener_calificacion(a_db, str(a_resultado.inserted_id))


def a_actualizar_calificacion(a_db: Database, a_id_calificacion: str, a_datos: A_CalificacionUpdate) -> Dict[str, Any]:
    a_obtener_calificacion(a_db, a_id_calificacion)
    a_cambios = a_datos.model_dump(exclude_none=True)
    if a_cambios:
        A_Calificacion.a_tabla(a_db).update_one({"_id": a_convertir_id(a_id_calificacion)}, {"$set": a_cambios})
    return a_obtener_calificacion(a_db, a_id_calificacion)


def a_eliminar_calificacion(a_db: Database, a_id_calificacion: str) -> Dict[str, str]:
    a_obtener_calificacion(a_db, a_id_calificacion)
    A_Calificacion.a_tabla(a_db).delete_one({"_id": a_convertir_id(a_id_calificacion)})
    return {"mensaje": f"Calificación con ID {a_id_calificacion} eliminada exitosamente", "tipo_borrado": "FISICO"}


def a_calificaciones_por_producto(a_db: Database, a_id_producto: int) -> Dict[str, Any]:
    """RF12: calificaciones de un producto y su promedio."""
    a_documentos = [a_formatear(a_d) for a_d in A_Calificacion.a_tabla(a_db).find({"productos.id_producto": a_id_producto})]

    a_notas = []
    a_nombre_producto = None
    for a_doc in a_documentos:
        for a_p in a_doc["productos"]:
            if a_p["id_producto"] == a_id_producto:
                a_notas.append(a_p["calificacion"])
                a_nombre_producto = a_nombre_producto or a_p["nombre"]

    return {
        "id_producto": a_id_producto,
        "nombre_producto": a_nombre_producto,
        "promedio_calificacion": round(sum(a_notas) / len(a_notas), 2) if a_notas else 0.0,
        "total_evaluaciones": len(a_notas),
        "calificaciones": a_documentos,
    }
