from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_ProductoMasVendidoItem,
    A_ReporteVentasResponse,
)
from app.controllers import a_controllers

a_reportes_router = APIRouter(
    prefix="/reportes",
    tags=["Reportes de Negocio"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_reportes_router.get(
    "/ventas",
    response_model=A_ReporteVentasResponse,
    status_code=status.HTTP_200_OK,
    summary="Reporte de ventas por rango de fechas",
    description="Retorna el monto total vendido y el número de pedidos entregados en un rango de fechas (RF11). (solo ADMIN).",
    responses={
        200: {"description": "Métricas de ventas obtenidas"},
    },
)
def a_reporte_ventas(
    desde: Optional[str] = Query(None, description="Fecha inicial en formato ISO (ej. 2026-10-01)"),
    hasta: Optional[str] = Query(None, description="Fecha final en formato ISO (ej. 2026-10-31)"),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_reporte_ventas(a_db, desde, hasta)


@a_reportes_router.get(
    "/productos-mas-vendidos",
    response_model=List[A_ProductoMasVendidoItem],
    status_code=status.HTTP_200_OK,
    summary="Reporte de productos más vendidos",
    description="Retorna el ranking de productos con mayor número de unidades vendidas y total recaudado (RF11). (solo ADMIN).",
    responses={
        200: {"description": "Ranking de productos más vendidos"},
    },
)
def a_reporte_productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=100, description="Cantidad máxima de productos a incluir en el ranking"),
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_reporte_productos_mas_vendidos(a_db, limite)
