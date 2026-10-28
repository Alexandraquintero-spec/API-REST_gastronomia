from typing import Any, Dict, List, Optional
from pymongo.database import Database
from app.models.a_pedido import A_Pedido


def a_reporte_ventas(a_db: Database, a_desde: Optional[str] = None, a_hasta: Optional[str] = None) -> Dict[str, Any]:
    """RF11: total vendido y número de pedidos ENTREGADOS en un rango de fechas (YYYY-MM-DD)."""
    a_filtro: Dict[str, Any] = {"estado": "ENTREGADO"}
    a_rango: Dict[str, str] = {}
    if a_desde:
        a_rango["$gte"] = a_desde
    if a_hasta:
        # Las fechas se guardan como 'YYYY-MM-DDTHH:MM:SS'; se incluye el día completo de 'hasta'
        a_rango["$lte"] = f"{a_hasta}T23:59:59" if len(a_hasta) == 10 else a_hasta
    if a_rango:
        a_filtro["fecha_pedido"] = a_rango

    a_resultado = list(
        A_Pedido.a_tabla(a_db).aggregate(
            [
                {"$match": a_filtro},
                {"$group": {"_id": None, "total_ventas": {"$sum": "$total"}, "numero_pedidos": {"$sum": 1}}},
            ]
        )
    )
    a_totales = a_resultado[0] if a_resultado else {"total_ventas": 0.0, "numero_pedidos": 0}
    return {
        "total_ventas": round(float(a_totales["total_ventas"]), 2),
        "numero_pedidos": int(a_totales["numero_pedidos"]),
        "desde": a_desde,
        "hasta": a_hasta,
    }


def a_reporte_productos_mas_vendidos(a_db: Database, a_limite: int = 10) -> List[Dict[str, Any]]:
    """RF11: ranking de productos más vendidos en pedidos ENTREGADOS."""
    a_pipeline = [
        {"$match": {"estado": "ENTREGADO"}},
        {"$unwind": "$detalles"},
        {
            "$group": {
                "_id": "$detalles.id_producto",
                "cantidad_vendida": {"$sum": "$detalles.cantidad"},
                "total_recaudado": {"$sum": "$detalles.subtotal"},
            }
        },
        {"$sort": {"cantidad_vendida": -1}},
        {"$limit": a_limite},
        # Se toma el nombre actual del producto desde su colección
        {"$lookup": {"from": "productos", "localField": "_id", "foreignField": "id_producto", "as": "producto"}},
    ]
    return [
        {
            "id_producto": a_r["_id"],
            "nombre": a_r["producto"][0]["nombre"] if a_r["producto"] else "",
            "cantidad_vendida": int(a_r["cantidad_vendida"]),
            "total_recaudado": round(float(a_r["total_recaudado"]), 2),
        }
        for a_r in A_Pedido.a_tabla(a_db).aggregate(a_pipeline)
    ]
