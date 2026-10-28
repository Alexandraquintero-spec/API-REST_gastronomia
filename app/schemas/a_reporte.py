from typing import Optional
from pydantic import BaseModel


class A_ReporteVentasResponse(BaseModel):
    total_ventas: float
    numero_pedidos: int
    desde: Optional[str] = None
    hasta: Optional[str] = None


class A_ProductoMasVendidoResponse(BaseModel):
    id_producto: int
    nombre: str
    cantidad_vendida: int
    total_recaudado: float
