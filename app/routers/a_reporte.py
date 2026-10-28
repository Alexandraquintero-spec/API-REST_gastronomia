from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pymongo.database import Database
from app.controllers.a_reporte import a_reporte_productos_mas_vendidos, a_reporte_ventas
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_PATRON_FECHA
from app.schemas.a_reporte import A_ProductoMasVendidoResponse, A_ReporteVentasResponse

a_router = APIRouter(
    prefix="/api/v1/reportes",
    tags=["Reportes"],
    dependencies=[Depends(a_requerir_roles(["ADMIN"]))],
)


@a_router.get(
    "/ventas",
    response_model=A_ReporteVentasResponse,
    summary="Ventas por rango de fechas",
    description="Total vendido y número de pedidos ENTREGADOS entre 'desde' y 'hasta' (RF11).",
)
def a_ventas(
    desde: Optional[str] = Query(None, pattern=A_PATRON_FECHA, description="Fecha inicial (YYYY-MM-DD)"),
    hasta: Optional[str] = Query(None, pattern=A_PATRON_FECHA, description="Fecha final (YYYY-MM-DD)"),
    a_db: Database = Depends(a_get_db),
):
    return a_reporte_ventas(a_db=a_db, a_desde=desde, a_hasta=hasta)


@a_router.get(
    "/productos-mas-vendidos",
    response_model=List[A_ProductoMasVendidoResponse],
    summary="Productos más vendidos",
    description="Ranking de productos por cantidad vendida en pedidos ENTREGADOS (RF11).",
)
def a_mas_vendidos(
    limite: int = Query(10, ge=1, le=100, description="Cantidad de productos del ranking"),
    a_db: Database = Depends(a_get_db),
):
    return a_reporte_productos_mas_vendidos(a_db=a_db, a_limite=limite)
